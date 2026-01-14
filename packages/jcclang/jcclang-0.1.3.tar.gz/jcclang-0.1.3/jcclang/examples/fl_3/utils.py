import json
import logging
import time
from typing import Optional, Tuple, Dict, Any

import requests
import trio

from jcclang.core.jobhub import rpc
from jcclang.examples.fl_3.const import LEADER_PREFIX

HEARTBEAT_TIMEOUT = 15
STRAGGLER_TIMEOUT_SEC = 45

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def publish_heartbeat(cli, role: str = "candidate", job_id: str = None, interval: float = 5.0):
    while True:
        ts = int(time.time())
        logger.info(f"[Heartbeat] Publishing {role} heartbeat")
        try:
            if role == "leader":
                # Leader 更新全局 leader_info
                current_val, current_rev = await read_var(cli, "leader_info")
                if current_val:
                    info = json.loads(current_val)
                    # 只有本节点是当前 Leader 时才更新
                    if info.get("node_id") == job_id:
                        info["heartbeat_ts"] = ts
                        ok, _, _ = await write_var(cli, "leader_info", json.dumps(info), current_rev)
                        if not ok:
                            logger.info("[Heartbeat] Failed to update leader_info (maybe lost leadership)")
                else:
                    logger.info("[Heartbeat] No leader_info found, skipping")

                # await update_client_in_registry(cli, job_id, ts, "leader")
            else:
                # Candidate/Client 更新自己的心跳和注册表信息
                val = json.dumps({"ts": ts, "role": role})
                # 获取当前版本号
                current_val, current_rev = await read_var(cli, get_heartbeat_name(job_id))
                await write_var(cli, get_heartbeat_name(job_id), val, current_rev)

                # 更新客户端注册表
                await update_client_in_registry(cli, job_id, ts, "active")

        except Exception as e:
            logger.exception(f"[Heartbeat] Parse error: {e}")

        await trio.sleep(interval)


async def read_var(cli, name: str) -> Tuple[Optional[str], int]:
    try:
        req = rpc.VarGet(name)
        resp = await req.do(cli)

        if resp is None:
            logger.error(f"[VarGet] Received None response for '{name}'")
            return None, 0

        if isinstance(resp, rpc.CodeError):
            logger.error(f"[VarGet] CodeError for '{name}': {resp}")
            return None, 0

        if not (hasattr(resp, 'value') and hasattr(resp, 'revision')):
            logger.error(f"[VarGet] Invalid response object for '{name}': {resp!r}")
            return None, 0

        return resp.value, resp.revision

    except trio.Cancelled:
        logger.exception(f"[VarGet] Cancelled for '{name}'")
        raise
    except Exception as e:
        logger.exception(f"[VarGet] Failed to read variable '{name}': {e}")
        return None, 0


async def write_var(cli, name: str, value: str, expected_rev: int) -> Tuple[bool, int, str]:
    req = rpc.VarSet(name, value, expected_rev)
    if expected_rev == 0:
        req = rpc.VarSet(name, value)
    resp = await req.do(cli)
    if isinstance(resp, rpc.CodeError):
        logger.error(f"[VarSet] Error: {resp}")
        return False, expected_rev, value
    # logger.info(f"[VarSet] OK: {resp}")
    return resp.ok, resp.revision, resp.value


# ----------------------------
# Client Registry Functions
# ----------------------------

# 客户端注册表名称
CLIENT_REGISTRY_KEY = "client_registry"


async def get_client_registry(cli) -> Tuple[Dict[str, Any], int]:
    """获取客户端注册表"""
    val, rev = await read_var(cli, CLIENT_REGISTRY_KEY)
    if val is None or val == "":
        # 如果注册表不存在，创建一个新的
        registry = {
            "clients": {},
            "next_client_rev": 1  # 客户端条目的下一个版本号
        }
        return registry, 0
    try:
        registry = json.loads(val)
        # 确保注册表结构完整
        if "clients" not in registry:
            registry["clients"] = {}
        if "next_client_rev" not in registry:
            registry["next_client_rev"] = 1
        return registry, rev
    except json.JSONDecodeError as e:
        logger.error(f"[Registry] Failed to parse client registry: {e}")
        return {"clients": {}, "next_client_rev": 1}, 0


async def update_client_in_registry(cli, client_id: str, heartbeat_ts: int, status: str = "active") -> bool:
    """更新注册表中的客户端信息（使用乐观锁）"""
    max_retries = 3
    for retry in range(max_retries):
        try:
            # 读取当前注册表
            registry, current_rev = await get_client_registry(cli)

            # 更新客户端信息
            if client_id not in registry["clients"]:
                # 新客户端
                registry["clients"][client_id] = {
                    "last_heartbeat": heartbeat_ts,
                    "status": status,
                    "revision": registry["next_client_rev"]
                }
                registry["next_client_rev"] += 1
            else:
                # 现有客户端，更新信息
                registry["clients"][client_id]["last_heartbeat"] = heartbeat_ts
                registry["clients"][client_id]["status"] = status
                registry["clients"][client_id]["revision"] += 1

            # 尝试写入更新后的注册表（使用乐观锁）
            ok, new_rev, new_val = await write_var(cli, CLIENT_REGISTRY_KEY, json.dumps(registry), current_rev)
            if ok:
                logger.debug(f"[Registry] Updated client {client_id} in registry, new revision: {new_rev}")
                return True
            else:
                logger.debug(
                    f"[Registry] Failed to update client {client_id} (version conflict), retry {retry + 1}/{max_retries}")
                await trio.sleep(0.1)  # 短暂等待后重试
        except Exception as e:
            logger.error(f"[Registry] Error updating client {client_id}: {e}")
            await trio.sleep(0.1)

    logger.error(f"[Registry] Failed to update client {client_id} after {max_retries} retries")
    return False


async def isolate_client_in_registry(cli, client_id: str) -> bool:
    """在注册表中将客户端标记为隔离状态（使用乐观锁）"""
    max_retries = 3
    for retry in range(max_retries):
        try:
            # 读取当前注册表
            registry, current_rev = await get_client_registry(cli)

            # 检查客户端是否存在
            if client_id in registry["clients"]:
                # 更新客户端状态为隔离
                registry["clients"][client_id]["status"] = "isolated"
                registry["clients"][client_id]["revision"] += 1

                # 尝试写入更新后的注册表（使用乐观锁）
                ok, new_rev, new_val = await write_var(cli, CLIENT_REGISTRY_KEY, json.dumps(registry), current_rev)
                if ok:
                    logger.info(f"[Registry] Isolated client {client_id} in registry")
                    return True
                else:
                    logger.debug(
                        f"[Registry] Failed to isolate client {client_id} (version conflict), retry {retry + 1}/{max_retries}")
                    await trio.sleep(0.1)
            else:
                logger.warning(f"[Registry] Client {client_id} not found in registry")
                return False
        except Exception as e:
            logger.error(f"[Registry] Error isolating client {client_id}: {e}")
            await trio.sleep(0.1)

    logger.error(f"[Registry] Failed to isolate client {client_id} after {max_retries} retries")
    return False


async def get_active_clients_from_registry(cli, heartbeat_timeout: int) -> list[str]:
    """从注册表获取活跃客户端列表"""
    try:
        registry, _ = await get_client_registry(cli)
        current_time = time.time()
        active_clients = []

        logger.info(f"[Registry] Checking {len(registry['clients'])} clients")

        for client_id, client_info in registry["clients"].items():
            logger.info(f"[Registry] Checking client {client_id}, and info is {client_info}")
            # 检查客户端状态和心跳时间
            if client_info["status"] == "active" and \
                    (current_time - client_info["last_heartbeat"]) < heartbeat_timeout:
                logger.info(f"[Registry] Client {client_id} is active")
                active_clients.append(client_id)

        logger.info(f"[Registry] Found {len(active_clients)} active clients: {active_clients}")
        return active_clients
    except Exception as e:
        logger.error(f"[Registry] Error getting active clients: {e}")
        return []


async def write_stream(cli, job_id: str, name: str, value: bytes) -> bool:
    logger.info(f"[Stream] Writing to {name}, value size {len(value)}")
    try:
        stream = await cli.open_stream(job_id, name)
        logger.info(f"Opened stream to {name} for model")
        await stream.write(value)
        await stream.close()
        logger.info(f"Model sent to {name}")
        return True
    except Exception as e:
        logger.error(f"Failed to send model to {name}: {e}")
        return False


async def receive_stream(cli, name, timeout=30) -> Tuple[str, bytes, float]:
    start_wait = time.time()
    try:
        # 注意：Leader 是接收方，需 accept_stream
        logger.info(f"[Stream] Waiting for model from {name} (timeout: {timeout}s)")

        stream = await cli.accept_stream(name)
        logger.info(f"[Stream] Connected to {name}, reading data...")

        data = await stream.read()
        await stream.close()
        elapsed = time.time() - start_wait
        logger.info(f"[Stream] Received {len(data)} bytes from {name} in {elapsed:.2f}s")
        return name, data, elapsed
    except trio.TooSlowError:
        elapsed = time.time() - start_wait
        logger.error(f"[Stream] Operation timed out after {elapsed:.2f}s from {name}")
        raise
    except Exception as e:
        elapsed = time.time() - start_wait
        logger.error(f"[Stream] Error receiving from {name} in {elapsed:.2f}s: {e}")
        raise


async def is_leader_alive(cli) -> bool:
    info = await get_leader_info(cli)
    if not info:
        return False

    diff = int(time.time()) - info.get("heartbeat_ts", 0)
    logger.info(f"[Heartbeat] Leader {info['node_id']} heartbeat: {diff}")
    return diff < HEARTBEAT_TIMEOUT


async def get_leader_info(cli) -> Optional[Dict[str, Any]]:
    v, _ = await read_var(cli, "leader_info")
    if not v:
        return None
    return json.loads(v) if v else None


async def is_client_alive(cli, job_id) -> bool:
    info = await get_client_info(cli, job_id)
    if not info:
        return False

    diff = int(time.time()) - info.get("ts", 0)
    logger.info(f"[Heartbeat] Client {job_id} heartbeat: {diff}")
    return diff < HEARTBEAT_TIMEOUT


async def get_client_info(cli, job_id) -> Optional[Dict[str, Any]]:
    v, _ = await read_var(cli, get_heartbeat_name(job_id))
    return json.loads(v) if v else None


def get_heartbeat_name(job_id) -> str:
    return f"heartbeat_{job_id}"


# ----------------------------
# Leader 选举
# ----------------------------
async def try_become_leader(cli, job_id: str) -> bool:
    current_value, current_rev = await read_var(cli, "leader_info")

    if current_value:
        try:
            leader = json.loads(current_value)

            # 检查是否有指定的leader
            if leader.get("designated"):
                designated_leader = LEADER_PREFIX + leader["node_id"]
                if designated_leader == job_id:
                    logger.info(f"[Leader] Current job {job_id} is the designated leader. Accepting leadership.")
                    # 更新leader_info，移除designated标记
                    updated_leader_info = {
                        "node_id": job_id,
                        "epoch": leader.get("epoch", 0) + 1,
                        "heartbeat_ts": int(time.time())
                    }
                    await write_var(cli, "leader_info", json.dumps(updated_leader_info), current_rev)
                    return True
                else:
                    logger.info(
                        f"[Leader] There is a designated leader {designated_leader}, which is not current job {job_id}. Not becoming leader.")
                    return False

            # 检查当前leader是否存活
            diff = int(time.time()) - leader.get("heartbeat_ts", 0)
            if diff < HEARTBEAT_TIMEOUT:
                return False
            else:
                logger.info(
                    f"[Leader] Leader {leader['node_id']} is not alive, current diff {diff}, and heartbeat timeout is {HEARTBEAT_TIMEOUT}")
        except Exception as e:
            logger.exception(f"[Leader] Error parsing leader_info: {e}")

    # 正常选举流程
    new_epoch = current_rev
    claim = {"node_id": job_id, "epoch": new_epoch, "heartbeat_ts": int(time.time())}
    logger.info(f"[Leader] Claiming leader with: {claim}")
    ok, actual_rev, actual_val = await write_var(cli, "leader_info", json.dumps(claim), new_epoch)

    if ok and actual_rev == (new_epoch + 1):
        logger.info(f"[Leader] Became leader with claim: {claim}")
        return True

    logger.info(f"[Leader] Failed to claim leader: {ok}, {actual_rev}, {actual_val}")
    return False


async def schedule_data(cluster_id, package_id):
    logger.info(f"[Schedule] Scheduling data for cluster {cluster_id}")
    return True, 123


async def schedule_data2(cluster_id, package_id):
    url = "http://localhost:7891/jobSet/binding"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "BearereyJ0eXAiOiJKV1Qi"
    }
    data = {
        "userID": 165,
        "info": {
            "type": "dataset",
            "packageID": package_id,
            "clusterIDs": [
                cluster_id
            ]
        }
    }
    resp = requests.post(url, headers=headers, json=data)
    if resp.status_code == 200:
        logger.info(resp.json())
        return True, resp.json().get('data', {}).get('bindingID', [])
    else:
        logger.info(resp.text)
        return False, 0


async def query_and_find_root_path(cluster_id, binding_id=13181):
    logger.info(f"[Query] Querying for root path for cluster {cluster_id}")
    return "./client_data_raw/block_0.pkl"


async def query_and_find_root_path2(cluster_id, binding_id=13181):
    """
    发送API请求并查找指定clusterID的rootPath

    Args:
        cluster_id (str): 要查找的clusterID
        user_id (int): 用户ID
        binding_id (int): 包ID

    Returns:
        str or None: 匹配成功返回rootPath，否则返回None
    """
    url = "http://localhost:7891/jobSet/queryUploaded"
    headers = {
        "Content-Type": "application/json",
    }
    user_id = 1
    data = {
        "queryParams": {
            "dataType": "dataset",
            "userID": user_id,
            "packageID": binding_id,
            "path": "",
            "CurrentPage": 1,
            "pageSize": 10,
            "orderBy": "time"
        }
    }

    try:
        # 发送POST请求
        response = requests.post(url, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            response_data = response.json()

            # 调用查找函数
            root_path = find_root_path_by_cluster_id(response_data, cluster_id)

            if root_path:
                print(f"成功找到clusterID: {cluster_id} 对应的rootPath: {root_path}")
            else:
                print(f"未找到clusterID: {cluster_id} 对应的rootPath")

            return root_path
        else:
            print(f"API请求失败，状态码: {response.status_code}")
            return None

    except Exception as e:
        print(f"请求过程中发生错误: {e}")
        return None


def find_root_path_by_cluster_id(response_data, target_cluster_id):
    """
    从返回的响应数据中查找指定clusterID对应的rootPath

    Args:
        response_data (dict): API返回的完整数据
        target_cluster_id (str): 要匹配的clusterID

    Returns:
        str or None: 匹配成功返回rootPath，否则返回None
    """
    try:
        # 获取uploadedDatas数组
        uploaded_datas = response_data.get('data', {}).get('uploadedDatas', [])

        # 遍历每个uploadedData
        for uploaded_data in uploaded_datas:
            # 获取uploadedCluster数组
            uploaded_clusters = uploaded_data.get('uploadedCluster', [])

            # 遍历每个cluster查找匹配
            for cluster in uploaded_clusters:
                if cluster.get('clusterID') == target_cluster_id:
                    return cluster.get('rootPath')

        # 没有找到匹配的clusterID
        return None

    except Exception as e:
        print(f"解析数据时发生错误: {e}")
        return None
