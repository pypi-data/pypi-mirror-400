import json
import random
import time
from collections import defaultdict, deque
from typing import Optional, Dict, List

import trio

from jcclang.examples.fl_3.const import LEADER_PREFIX, INITIAL_MODEL_FROM_CLIENT, FL_CONFIG, DATA_OWNER
from jcclang.examples.fl_3.model import deserialize_model, serialize_model, aggregate_models
from jcclang.examples.fl_3.utils import (
    logger, write_var, read_var, write_stream, receive_stream, get_active_clients_from_registry,
    isolate_client_in_registry,
    publish_heartbeat, schedule_data, query_and_find_root_path
)

# ----------------------------
# 配置常量（可从 config.yaml 加载）
# ----------------------------
MAX_ROUNDS = 50
LOCAL_EPOCHS = 3
LEARNING_RATE = 0.01
CHECKPOINT_INTERVAL = 10

STRAGGLER_TIMEOUT_SEC = 45
MIN_SAMPLES_THRESHOLD = 10
MIGRATION_COOLDOWN_ROUNDS = 5


# ----------------------------
# 全局状态（Leader 内存中）
# ----------------------------
class LeaderState:
    def __init__(self):
        self.current_round = 0
        self.global_model = None  # PyTorch model or equivalent

        # 数据归属：client_id -> [data_block_id]
        # self.data_ownership: Dict[str, List[str]] = {}
        # self.data_metadata: Dict[str, Dict] = {}  # block_id -> metadata

        # 客户端画像：滑动窗口记录最近性能
        self.client_profiles = defaultdict(lambda: {
            'response_times': deque(maxlen=3),
            'num_samples': 0,
            'last_active_round': 0,
            'migrated_at_round': -100  # 用于冷却期
        })

        self.isolated_clients: set = set()  # 永久剔除列表
        self.active_clients: List[str] = []


# ----------------------------
# 辅助函数
# ----------------------------
def load_initial_ownership(config_path: str) -> tuple[Dict, Dict]:
    """从配置文件加载初始 data_ownership 和 metadata"""
    with open(config_path) as f:
        cfg = json.load(f)
    return cfg["ownership"], cfg["metadata"]


def save_checkpoint(state: LeaderState, path: str):
    """将模型 + 状态保存到本地磁盘（非 OBS）"""
    import torch
    ckpt = {
        'round': state.current_round,
        'model_state_dict': state.global_model.state_dict(),
        # 'data_ownership': state.data_ownership,
        # 'data_metadata': state.data_metadata,
        'isolated_clients': list(state.isolated_clients)
    }
    torch.save(ckpt, path)


def load_checkpoint(path: str, model_template):
    """从 checkpoint 恢复状态"""
    import torch
    ckpt = torch.load(path)
    model_template.load_state_dict(ckpt['model_state_dict'])

    state = LeaderState()
    state.current_round = ckpt['round']
    state.global_model = model_template
    # state.data_ownership = ckpt['data_ownership']
    # state.data_metadata = ckpt['data_metadata']
    state.isolated_clients = set(ckpt['isolated_clients'])
    return state


async def gather_with_timeout(active_clients, tasks, timeout):
    results = {}
    errors = {}

    logger.info(f"[Leader] gather_with_timeout started with timeout {timeout}s")

    try:
        with trio.fail_after(timeout):
            async with trio.open_nursery() as nursery:
                for cid, task in zip(active_clients, tasks):
                    logger.info(f"[Leader] Receiving model from {cid}")

                    async def handle_task(t=task, cid=cid):
                        try:
                            results[cid] = await t
                        except Exception as e:
                            logger.error(f"[Leader] Error from {cid}: {e}")
                            errors[cid] = e

                    nursery.start_soon(handle_task)

        logger.info("[Leader] All tasks completed before timeout")

    except trio.TooSlowError:
        logger.info(f"[Leader] Timeout after {timeout}s")

    logger.info(f"[Leader] Finished: {len(results)} ok, {len(errors)} errors")
    return results, errors


def detect_stragglers(state: LeaderState, current_round: int) -> List[str]:
    """检测慢节点"""
    stragglers = []
    for cid, profile in state.client_profiles.items():
        logger.info(f"[Leader] detect stragglers, client {cid} profile: {profile}")
        if cid in state.isolated_clients:
            continue
        if profile['last_active_round'] != current_round:
            continue  # 本轮未参与

        avg_time = sum(profile['response_times']) / len(profile['response_times'])
        logger.info(
            f"[Leader] detect stragglers, client {cid} avg_time: {avg_time}, and timeout is {STRAGGLER_TIMEOUT_SEC}")
        too_slow = avg_time > STRAGGLER_TIMEOUT_SEC
        too_few_samples = profile['num_samples'] < MIN_SAMPLES_THRESHOLD

        logger.info(
            f"[Leader] detect stragglers, client {cid} too_slow: {too_slow}, too_few_samples: {too_few_samples}")

        if too_slow or too_few_samples:
            # 检查冷却期
            if current_round - profile['migrated_at_round'] > MIGRATION_COOLDOWN_ROUNDS:
                stragglers.append(cid)
    return stragglers


def select_target_client(state: LeaderState, exclude: str, candidates: List[str]) -> Optional[str]:
    """选择负载最低的目标 client"""
    logger.info(f"[Leader] Select target client from {candidates}")
    if len(candidates) == 1:
        return candidates[0]

    valid_targets = [c for c in candidates if c != exclude and c not in state.isolated_clients]
    logger.info(f"[Leader] Select valid target client from {valid_targets}")
    if not valid_targets:
        return None

    # 按 num_samples 升序
    valid_targets.sort(key=lambda c: state.client_profiles[c]['num_samples'])
    return valid_targets[0]


async def get_active_clients(jobhub_cli, state: LeaderState, heartbeat_timeout: int = 30) -> List[str]:
    """
    从客户端注册表中获取活跃客户端列表
    基于心跳时间、状态和数据所有权判断
    """
    # 1. 从注册表获取所有活跃客户端
    registry_active_clients = await get_active_clients_from_registry(jobhub_cli, heartbeat_timeout)

    # 2. 过滤掉被隔离的客户端和没有数据分配的客户端
    filtered_clients = []
    for cid in registry_active_clients:
        # 检查客户端是否被隔离
        if cid in state.isolated_clients:
            continue

        # 检查客户端是否有数据分配
        data_owner = await read_var(jobhub_cli, DATA_OWNER + cid)
        logger.info(f"[Leader] Data owner of {cid}: {data_owner}")
        if data_owner:
            filtered_clients.append(cid)

    logger.info(f"[Leader] Active clients from registry: {registry_active_clients}")
    logger.info(f"[Leader] Filtered active clients (excluding isolated/no-data): {filtered_clients}")

    return filtered_clients


async def evaluate_performance(state: LeaderState, job_id: str) -> Dict[str, float]:
    """评估所有活跃客户端和leader的性能"""
    performances = {}

    logger.info(
        f"[Leader] Evaluating performance for {len(state.active_clients)} active clients, profiles: {state.client_profiles}")

    # 计算每个活跃客户端的平均响应时间（越小越好）
    for cid in state.active_clients:
        if cid in state.client_profiles and state.client_profiles[cid]['response_times']:
            avg_response_time = sum(state.client_profiles[cid]['response_times']) / len(
                state.client_profiles[cid]['response_times'])
            performances[cid] = avg_response_time
        else:
            # 新客户端，给一个较高的初始值
            performances[cid] = float('inf')

    # 添加leader自身的性能评估
    # 注意：leader的性能信息可能需要单独维护，这里假设leader的性能是所有客户端中最好的
    # 实际实现中，leader可能需要监控自身的性能指标
    performances[job_id] = min(performances.values()) if performances else 0

    logger.info(f"[Leader] Performance evaluation: {performances}")
    return performances


async def check_and_switch_leader(job_id: str, jobhub_cli, state: LeaderState) -> bool:
    """检查性能并在需要时切换leader"""
    if state.current_round % 3 != 0:
        return False

    logger.info(f"[Leader] Round {state.current_round} is a performance check round")

    # 评估所有客户端和leader的性能
    performances = await evaluate_performance(state, job_id)
    if not performances:
        logger.info("[Leader] No clients available for performance evaluation")
        return False

    logger.info(f"[Leader] Performance evaluation results: {performances}")

    # 找出性能最好的（响应时间最短的）
    best_performer = min(performances, key=performances.get)

    logger.info(f"[Leader] Best performer: {best_performer} with response time: {performances[best_performer]:.2f}s")

    # 如果自身不是性能最好的，切换leader
    best_performer_id = LEADER_PREFIX + best_performer
    if best_performer_id != job_id:
        logger.info(f"[Leader] Current leader {job_id} is not the best performer. Switching to {best_performer}")

        # 先将最新的全局模型分发给所有活跃客户端
        if state.active_clients:
            logger.info("[Leader] Distributing latest global model to all active clients before switching...")
            model_bytes = serialize_model(state.global_model)
            for cid in state.active_clients:
                try:
                    logger.info(f"Sending latest model to {cid}")
                    await write_stream(jobhub_cli, cid, f"model_to_{cid}", model_bytes)
                except Exception as e:
                    logger.warning(f"Failed to send latest model to {cid}: {e}")
            logger.info("[Leader] All active clients have received the latest model.")

        # 在全局变量中指定新的leader
        # 创建一个新的leader_info，指定best_performer为新leader
        leader_info = {
            "node_id": best_performer,
            "epoch": int(time.time()),
            "heartbeat_ts": int(time.time()),
            "designated": True  # 标记为指定的leader
        }

        # 获取当前版本号并更新leader_info
        current_val, current_rev = await read_var(jobhub_cli, "leader_info")
        await write_var(jobhub_cli, "leader_info", json.dumps(leader_info), current_rev)

        logger.info(f"[Leader] Leader switched to {best_performer}. Terminating current leader thread.")
        return True

    logger.info(f"[Leader] Current leader {job_id} is the best performer. Continuing...")
    return False


async def run_as_leader(
        job_id,
        jobhub_cli,
        scheduler,
        model_template,
        initial_config_path: str,
        checkpoint_path: Optional[str] = None
):
    async with trio.open_nursery() as nursery:
        # 启动独立的心跳任务
        nursery.start_soon(publish_heartbeat, jobhub_cli, "leader", job_id, 5.0)
        try:
            await start_leader(job_id, jobhub_cli, scheduler, model_template, initial_config_path, checkpoint_path)
        except Exception as e:
            logger.info(f"[Leader] Leader thread terminated: {e}")
            nursery.cancel_scope.cancel()
        return True


# ----------------------------
# 主 Leader 逻辑
# ----------------------------
async def start_leader(
        job_id,
        jobhub_cli,
        scheduler,
        model_template,
        initial_config_path: str,
        checkpoint_path: Optional[str] = None
):
    state = LeaderState()

    # 这里用于测试
    # owner_ship_test = {
    #     "ownership": [
    #         {
    #             "packageID": 11421,
    #             "clusterID": "1790300942428540928",
    #             "path": r'D:\Work\Codes\workspace\workspace\JCWeaver\jcclang\test_data\client_data_raw\block_1.pkl'
    #         }
    #     ]
    # }
    # await write_var(jobhub_cli, DATA_OWNER + "client_1", json.dumps(owner_ship_test), 0)
    # await write_var(jobhub_cli, DATA_OWNER + "client_2", json.dumps(owner_ship_test), 0)

    # ---- 初始化状态 ----
    logger.info("[Leader] Initializing leader state...")
    state.global_model = model_template
    # ownership, metadata = load_initial_ownership(initial_config_path)
    # state.data_ownership = ownership
    # state.data_metadata = metadata
    state.current_round = 0

    # 广播全局配置（KV）
    fl_config = {
        "max_rounds": MAX_ROUNDS,
        "local_epochs": LOCAL_EPOCHS,
        "learning_rate": LEARNING_RATE
    }
    await write_var(jobhub_cli, FL_CONFIG, json.dumps(fl_config), 0)

    # 发布初始数据归属（KV）
    # version = str(int(time.time() * 1e6))
    # await write_var(jobhub_cli, DATA_OWNERSHIP_VERSION, version, 0)
    # ownership_payload = {
    #     "ownership": state.data_ownership,
    #     "metadata": state.data_metadata
    # }
    # await write_var(jobhub_cli, f"data_ownership_v{version}", json.dumps(ownership_payload), 0)

    # 等待活跃客户端并决定模型初始化方式
    logger.info("[Leader] Waiting for active clients to determine model initialization...")
    max_wait_time = 5
    start_time = time.time()
    active_clients_found = False

    while time.time() - start_time < max_wait_time:
        state.active_clients = await get_active_clients(jobhub_cli, state)
        if state.active_clients:
            active_clients_found = True
            break
        logger.info("[Leader] No active clients yet. Waiting...")
        await trio.sleep(5)

    if active_clients_found:
        logger.info(f"Active clients found: {state.active_clients}")

        # 检查活跃客户端中是否有与当前job_id相同的客户端
        # 新leader所在节点必然有client，可以从这个client获取模型
        local_client = None
        for cid in state.active_clients:
            leader_id = LEADER_PREFIX + cid
            if leader_id == job_id:
                local_client = cid
                break

        # 如果没有本地客户端，选择第一个活跃客户端
        if not local_client:
            local_client = state.active_clients[0]

        logger.info(f"Getting initial model from client {local_client}...")
        try:
            # 尝试从客户端获取初始模型
            # 使用特殊的流名称表示请求初始模型
            # initial_model_name = f"initial_model_from_{local_client}"
            logger.info(f"Waiting for initial model stream: {INITIAL_MODEL_FROM_CLIENT}")

            # 指定INITIAL_MODEL_FROM_CLIENT
            # 构建json string
            initial_model_name = json.dumps({
                "client_id": local_client,
                "leader_id": job_id
            })
            await write_var(jobhub_cli, INITIAL_MODEL_FROM_CLIENT, initial_model_name, 0)

            # 尝试打开流获取初始模型
            _, model_bytes, _ = await receive_stream(jobhub_cli, INITIAL_MODEL_FROM_CLIENT)

            # 接收完成后，要将INITIAL_MODEL_FROM_CLIENT置空
            # await write_var(jobhub_cli, INITIAL_MODEL_FROM_CLIENT, "", 0)

            if model_bytes:
                # 反序列化并设置为全局模型
                state_dict = deserialize_model(model_bytes)
                state.global_model.load_state_dict(state_dict)
                logger.info("[Leader] Successfully received initial model from client.")
            else:
                logger.warning("No initial model received. Initializing new model.")
                # 初始化新模型
                state.global_model = model_template
                logger.info("[Leader] Initialized new global model.")
        except Exception as e:
            logger.warning(f"Failed to get initial model from client: {e}. Initializing new model.")
            # 初始化新模型
            state.global_model = model_template
            logger.info("[Leader] Initialized new global model.")
    else:
        logger.info("[Leader] No active clients found after waiting. Initializing new model.")
        # 初始化新模型
        state.global_model = model_template
        logger.info("[Leader] Initialized new global model.")

    logger.info(f"[Leader] Leader started at round {state.current_round}. Active clients will be discovered.")

    # ---- 主训练循环 ----
    while state.current_round < MAX_ROUNDS:

        # 从心跳数据中获取活跃客户端
        state.active_clients = await get_active_clients(jobhub_cli, state)
        logger.info(f"[Leader] Active clients (based on heartbeat): {state.active_clients}")

        if not state.active_clients:
            logger.info("[Leader] No active clients! Continue..")
            await trio.sleep(2)
            continue

        state.current_round += 1
        logger.info(f"[Leader] \n--- Leader round {state.current_round} ---")

        # ==============================
        # 2. 分发全局模型（使用 STREAM）
        # ==============================
        model_bytes = serialize_model(state.global_model)

        # 跟踪成功接收模型的客户端
        clients_received_model = []

        for cid in state.active_clients:
            logger.info(f"[Leader] Sending model to {cid}")
            stream_name = f"model_to_{cid}"
            ok = await write_stream(jobhub_cli, cid, stream_name, model_bytes)

            if ok:
                clients_received_model.append(cid)
                logger.info(f"[Leader] Successfully sent model to {cid}")
            else:
                logger.warning(f"[Leader] Failed to send model to {cid}")

        logger.info(
            f"[Leader] Model dispatched to {len(clients_received_model)}/{len(state.active_clients)} clients via streams.")

        # ==============================
        # 3. 等待客户端提交模型（使用 STREAM）
        # ==============================
        submissions = {}

        # 如果没有客户端成功接收模型，跳过当前轮次
        if not clients_received_model:
            logger.warning("[Leader] No clients received model. Skipping round.")
            await trio.sleep(5)
            continue

        # 只等待那些成功接收模型的客户端
        recv_tasks = []
        for cid in clients_received_model:
            recv_tasks.append(receive_stream(jobhub_cli, f"model_from_{cid}"))

        logger.info(
            f"[Leader] Round {state.current_round}, waiting for {len(clients_received_model)} clients to submit models...")

        # 等待前更新全局变量leader_round，用于调试
        await write_var(jobhub_cli, "leader_round", f"{state.current_round}", 0)

        # 并发接收模型
        results, errors = await gather_with_timeout(clients_received_model, recv_tasks, STRAGGLER_TIMEOUT_SEC + 20)
        logger.info(f"[Leader] Received {len(results)} models from {len(clients_received_model)} clients.")

        # 处理结果
        for cid, (cid_result, model_data, elapsed) in results.items():
            logger.info(f'cid: {cid}, cid_result: {cid_result}, model_data size: {len(model_data)}, elapsed: {elapsed}')
            submissions[cid] = deserialize_model(model_data)

            profile = state.client_profiles[cid]
            logger.info(f"[Leader] Profile for {cid_result}: {profile}")
            profile['response_times'].append(elapsed)
            profile['last_active_round'] = state.current_round
            # total_samples = sum(state.data_metadata[bid]['size'] for bid in state.data_ownership[cid_result])
            # profile['num_samples'] = total_samples
            # 随机生成5-15的数
            profile['num_samples'] = random.randint(5, 15)

            logger.info(f"[Leader] Received model from {cid_result} (time={elapsed:.2f}s)")
            logger.info(f"client profile: {profile}")

        # 处理超时或错误
        for cid, error in errors.items():
            logger.warning(f"Failed to receive model from {cid}: {error}")

        logger.info(f"[Leader] Models received, submissions size: {len(submissions)}")
        # 4. 聚合模型（FedAvg）
        if submissions:
            weights = []
            models = []
            for cid, model in submissions.items():
                w = state.client_profiles[cid]['num_samples']
                weights.append(w)
                models.append(model)
            logger.info("[Leader] Aggregating models...")
            state.global_model = aggregate_models(models, weights, state.global_model)
            logger.info("[Leader] Model aggregated successfully.")
        else:
            logger.info("[Leader] No submissions received. Skipping aggregation.")

        # 5. Straggler 检测与数据迁移
        stragglers = detect_stragglers(state, state.current_round)
        logger.info(f"[Leader] Stragglers detected size: {len(stragglers)}")
        for slow_client in stragglers:
            logger.info(f"[Leader] Detected straggler: {slow_client}")

            target = select_target_client(state, slow_client, state.active_clients)
            logger.info(f"[Leader] Selected transfer target: {target}")

            if not target:
                logger.info(f"[Leader] No suitable target for {slow_client}. Isolating.")
                # 同时在注册表中标记客户端为隔离状态
                state.isolated_clients.add(slow_client)
                await isolate_client_in_registry(jobhub_cli, slow_client)
                continue

            if target == slow_client:
                logger.info(f"[Leader] {slow_client} is already the best client. Skipping.")
                continue

            # source_info = state.data_ownership[slow_client]
            # target_info = state.data_ownership[target]
            slow_client_data_owner = DATA_OWNER + slow_client
            target_data_owner = DATA_OWNER + target
            source_str, _ = await read_var(jobhub_cli, slow_client_data_owner)
            source_info = json.loads(source_str).get('ownership')
            target_str, _ = await read_var(jobhub_cli, target_data_owner)
            target_info = json.loads(target_str).get('ownership')
            logger.info(f"[Leader] Moving {source_info} from {slow_client} to {target}")

            data_num = len(target_info)
            if data_num == 0:
                logger.info(f"[Leader] No data to move to {target} from {slow_client}")
                continue

            cluster_id = target_info[0].get('clusterID')
            for info in source_info:
                package_id = info.get('packageID')
                logger.info(f"[Leader] Moving {package_id} from {slow_client} to {target}")
                success, binding_id = await schedule_data(cluster_id, package_id)
                if success:
                    data_path = await query_and_find_root_path(binding_id)
                    target_info.append({
                        "path": data_path,
                        "clusterID": cluster_id,
                        "packageID": package_id
                    })

            if len(target_info) > data_num:
                logger.info(f"[Leader] Migration successful for {slow_client}")
                # state.data_ownership[target].extend(target_info)
                # del state.data_ownership[slow_client]
                # 更新 ownership
                target_info_wrapped = {
                    "ownership": target_info
                }
                await write_var(jobhub_cli, target_data_owner, json.dumps(target_info_wrapped), 0)
                # 将迁移过的数据从源客户端中删除
                source_info = {
                    "ownership": []
                }
                await write_var(jobhub_cli, slow_client_data_owner, json.dumps(source_info), 0)
                logger.info(f"[Leader] Data ownership updated for {target}")

                state.client_profiles[slow_client]['migrated_at_round'] = state.current_round

                # 更新 ownership（KV）
                # new_ver = str(int(time.time() * 1e6))
                # payload = {
                #     "ownership": state.data_ownership,
                #     "metadata": state.data_metadata
                # }
                # await write_var(jobhub_cli, DATA_OWNERSHIP_VERSION, new_ver, 0)
                # await write_var(jobhub_cli, f"data_ownership_v{new_ver}", json.dumps(payload), 0)
                # logger.info(f"[Leader] Ownership updated. New version: {new_ver}")
            else:
                logger.info(f"[Leader] Migration failed for {slow_client}. Isolating.")
                state.isolated_clients.add(slow_client)
                # 同时在注册表中标记客户端为隔离状态
                await isolate_client_in_registry(jobhub_cli, slow_client)

        # 6. Checkpoint
        if state.current_round % CHECKPOINT_INTERVAL == 0:
            ckpt_file = f"checkpoint_round_{state.current_round}.pth"
            save_checkpoint(state, ckpt_file)
            logger.info(f"[Leader] Checkpoint saved to {ckpt_file}")

        # 7. 检查性能并在需要时切换leader
        if await check_and_switch_leader(job_id, jobhub_cli, state):
            # 如果返回True，表示需要切换leader，终止当前leader线程
            logger.info(f"[Leader] Leader switch initiated. Terminating current leader thread.")
            raise Exception("Leader switch requested")

    # ---- 训练结束（KV）----
    final_model_path = "final_global_model.pth"
    import torch
    torch.save(state.global_model.state_dict(), final_model_path)
    await write_var(jobhub_cli, "training_finished", "true", 0)
    logger.info(f"[Leader] Training completed. Final model saved to {final_model_path}")
