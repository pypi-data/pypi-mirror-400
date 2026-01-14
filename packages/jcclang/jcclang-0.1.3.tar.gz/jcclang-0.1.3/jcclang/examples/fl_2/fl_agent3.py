import json
import logging
import os
import pickle
import time
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, List

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import trio
from torch.utils.data import DataLoader, Subset, random_split
from torchvision import datasets
from torchvision import transforms

from jcclang.core.jobhub import JobHubClient, rpc

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ----------------------------
# 配置
# ----------------------------
JOBHUB_HOST = os.getenv("JOBHUB_HOST", "127.0.0.1")
JOBHUB_PORT = int(os.getenv("JOBHUB_PORT", "7901"))
SHARED_SECRET = os.getenv("JOBHUB_SECRET", "01234567890123456789012345678901").encode()

JOBSET_ID = os.getenv("JOBSET_ID", "fl_mnist")
SELF_JOB_ID = os.getenv("JOB_ID", "client_3")

OBS_BASE_DIR = os.getenv("OBS_BASE_DIR", "./fl_obs")
CLIENT_DATA_DIR = os.getenv("CLIENT_DATA_DIR", "./client_data")

FULL_DATASET = datasets.MNIST(root=f'D:\\Model\\dataset\\mnist_fl', train=True, download=False,
                              transform=transforms.Compose([
                                  transforms.ToTensor(),
                                  transforms.Normalize((0.1307,), (0.3081,))
                              ]))

HEARTBEAT_INTERVAL = 5
HEARTBEAT_TIMEOUT = 15
MAX_CLIENT_RETRIES = 3
TRAIN_EPOCHS = 2
BATCH_SIZE = 32

# 全局缓存，避免重复加载
_DATA_CACHE = {}


def get_data_loader(client_id: str, train: bool = True, batch_size: int = 32, shuffle: bool = True):
    """
    根据 client_id 加载其索引对应的数据，并动态划分 train/val。
    """
    global _DATA_CACHE

    cache_key = (client_id, train)
    if cache_key in _DATA_CACHE:
        dataset = _DATA_CACHE[cache_key]
    else:

        # 读取客户端的索引列表
        filepath = os.path.join("client_data", f"{client_id}.pkl")
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Data file not found: {filepath}")

        with open(filepath, "rb") as f:
            indices = pickle.load(f)  # list of int

        if not isinstance(indices, list) or not all(isinstance(i, int) for i in indices):
            raise ValueError(f"Expected list of int indices in {filepath}, got {type(indices)}")

        # 创建子集
        client_subset = Subset(FULL_DATASET, indices)

        # 动态划分 train/val（10% 验证）
        n_total = len(client_subset)
        n_val = max(1, int(0.1 * n_total))  # 至少 1 个样本
        n_train = n_total - n_val

        train_subset, val_subset = random_split(
            client_subset,
            [n_train, n_val],
            generator=torch.Generator().manual_seed(42)
        )

        dataset = train_subset if train else val_subset
        _DATA_CACHE[cache_key] = dataset

    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle if train else False,
        num_workers=0,
        pin_memory=False
    )
    return loader


val_loader = None


def init_validation_loader():
    global val_loader
    if val_loader is not None:
        return
    # 这里用 Leader 自己的 ID 加载验证集（例如 client_0 的部分数据作验证）
    val_loader = get_data_loader(SELF_JOB_ID, train=False)


def evaluate_model(model: torch.nn.Module, data_loader) -> float:
    """
    在验证集上计算平均 loss。
    返回 scalar loss（越小越好）。
    """
    model.eval()
    total_loss = 0.0
    total_samples = 0
    device = next(model.parameters()).device

    with torch.no_grad():
        for inputs, targets in data_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            outputs = model(inputs)
            loss = F.cross_entropy(outputs, targets)
            total_loss += loss.item() * inputs.size(0)
            total_samples += inputs.size(0)

    avg_loss = total_loss / total_samples if total_samples > 0 else float('inf')
    logger.info(f"[Eval] Validation Loss: {avg_loss:.4f}")
    return avg_loss


# ----------------------------
# 本地文件模拟 OBS
# ----------------------------
class OBSClient:
    def __init__(self, base_dir: str = "./fl_obs"):
        self.base_dir = Path(base_dir).resolve()
        self._lock = trio.Lock()  # 使用 trio.Lock 保证异步安全

    async def put_object(self, bucket: str, key: str, data: bytes) -> None:
        obj_path = self._get_path(bucket, key)
        await trio.to_thread.run_sync(self._write_file, obj_path, data)

    async def get_object(self, bucket: str, key: str) -> bytes:
        obj_path = self._get_path(bucket, key)
        return await trio.to_thread.run_sync(self._read_file, obj_path)

    def _get_path(self, bucket: str, key: str) -> Path:
        safe_key = str(Path(key).as_posix()).lstrip('/')
        if '..' in safe_key:
            raise ValueError("Invalid key")
        path = self.base_dir / bucket / safe_key
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def _write_file(self, path: Path, data: bytes):
        with open(path, 'wb') as f:
            f.write(data)

    def _read_file(self, path: Path) -> bytes:
        if not path.exists():
            return b""
        with open(path, 'rb') as f:
            return f.read()


obs_client = OBSClient(OBS_BASE_DIR)


# ----------------------------
# 全局变量操作
# ----------------------------
async def read_var(cli, name: str) -> Tuple[Optional[str], int]:
    req = rpc.VarGet(name)
    resp = await req.do(cli)
    if isinstance(resp, rpc.CodeError):
        logger.error(f"[VarGet] Error: {resp}")
        return None, 0
    return resp.value, resp.revision


async def write_var(cli, name: str, value: str, expected_rev: int) -> Tuple[bool, int, str]:
    req = rpc.VarSet(name, value, expected_rev)
    resp = await req.do(cli)
    if isinstance(resp, rpc.CodeError):
        logger.error(f"[VarSet] Error: {resp}")
        return False, expected_rev, value
    logger.info(f"[VarSet] OK: {resp}")
    return resp.ok, resp.revision, resp.value


# ----------------------------
# 心跳与 Leader 管理
# ----------------------------
async def publish_heartbeat(cli, role: str = "candidate"):
    ts = int(time.time())
    if role == "leader":
        # Leader 更新全局 leader_info
        current_val, current_rev = await read_var(cli, "leader_info")
        if current_val:
            try:
                info = json.loads(current_val)
                # 只有本节点是当前 Leader 时才更新
                if info.get("node_id") == SELF_JOB_ID:
                    info["heartbeat_ts"] = ts
                    ok, _, _ = await write_var(cli, "leader_info", json.dumps(info), current_rev)
                    if not ok:
                        logger.info("[Heartbeat] Failed to update leader_info (maybe lost leadership)")
            except Exception as e:
                logger.info(f"[Heartbeat] Parse error: {e}")
        else:
            logger.info("[Heartbeat] No leader_info found, skipping")
    else:
        # Candidate/Client 更新自己的心跳（可选，主要用于调试）
        val = json.dumps({"ts": ts, "role": role})
        await write_var(cli, f"heartbeat_{SELF_JOB_ID}", val, ts)


async def get_leader_info(cli) -> Optional[Dict[str, Any]]:
    v, _ = await read_var(cli, "leader_info")
    return json.loads(v) if v else None


async def is_leader_alive(cli) -> bool:
    info = await get_leader_info(cli)
    if not info:
        return False

    diff = int(time.time()) - info.get("heartbeat_ts", 0)
    logger.info(f"[Heartbeat] Leader {info['node_id']} heartbeat: {diff}")
    return diff < HEARTBEAT_TIMEOUT


# ----------------------------
# 模型定义
# ----------------------------
class SimpleCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 32, 3, 1)
        self.conv2 = nn.Conv2d(32, 64, 3, 1)
        self.dropout1 = nn.Dropout(0.25)
        self.dropout2 = nn.Dropout(0.5)
        self.fc1 = nn.Linear(9216, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = self.conv1(x)
        x = torch.relu(x)
        x = self.conv2(x)
        x = torch.relu(x)
        x = torch.max_pool2d(x, 2)
        x = self.dropout1(x)
        x = torch.flatten(x, 1)
        x = self.fc1(x)
        x = torch.relu(x)
        x = self.dropout2(x)
        x = self.fc2(x)
        return torch.log_softmax(x, dim=1)


def get_model_state_dict() -> dict:
    model = SimpleCNN()
    return model.state_dict()


def load_model_from_bytes(data: bytes) -> nn.Module:
    model = SimpleCNN()
    state_dict = pickle.loads(data)
    model.load_state_dict(state_dict)
    return model


def serialize_model(model: nn.Module) -> bytes:
    return pickle.dumps(model.state_dict())


# ----------------------------
# 客户端训练逻辑
# ----------------------------
async def train_local_model(model_bytes: bytes) -> bytes:
    """在本地数据上训练模型"""
    # 加载模型
    model = load_model_from_bytes(model_bytes)
    model.train()

    # 加载本客户端数据
    data_path = Path(CLIENT_DATA_DIR) / f"{SELF_JOB_ID}.pkl"
    if not data_path.exists():
        logger.info(f"[Train] No data for {SELF_JOB_ID}")
        return serialize_model(model)

    with open(data_path, "rb") as f:
        indices = pickle.load(f)

    subset = Subset(FULL_DATASET, indices)
    dataloader = DataLoader(subset, batch_size=BATCH_SIZE, shuffle=True)

    optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.5)
    criterion = nn.NLLLoss()

    for epoch in range(TRAIN_EPOCHS):
        for data, target in dataloader:
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()

    return serialize_model(model)


# ----------------------------
# Leader 聚合（FedAvg）
# ----------------------------
async def fed_avg_aggregate(cli, round_id: int, min_clients: int = 1, timeout_per_client: float = 20.0):
    """
    聚合客户端更新，最多等待 timeout_per_client * expected 但更灵活：
    - 每个 accept 最多等 timeout_per_client 秒
    - 收到 min_clients 个更新即可提前结束（可选）
    - 总体不强求固定数量
    """
    updates = []
    client_ids = []
    start_time = trio.current_time()

    logger.info(f"[Leader] Waiting for {min_clients} clients for round {round_id}")

    # 我们不知道确切有多少 client 会来，所以用“持续接受直到超时”
    while True:
        elapsed = trio.current_time() - start_time
        remaining = max(0.1, timeout_per_client - elapsed)

        if elapsed > timeout_per_client and len(updates) >= min_clients:
            logger.info(f"[Leader] Stopping aggregation (timeout). Got {len(updates)} updates.")
            break

        try:
            with trio.move_on_after(remaining) as cancel_scope:
                stream = await cli.accept_stream(f"round_{round_id}")

            if cancel_scope.cancelled_caught:
                if len(updates) == 0:
                    logger.info(f"[Leader] Timeout waiting for first client in round {round_id}.")
                else:
                    logger.info(f"[Leader] Timeout after receiving {len(updates)} clients.")
                break

            # 读取 client 信息
            try:
                cmd_bytes = await stream.receive_some(1024)
                if not cmd_bytes:
                    await stream.close()
                    continue
                cmd = json.loads(cmd_bytes.decode())
                client_id = cmd.get("client_id", "unknown")
            except Exception as e:
                client_id = "malformed"
                logger.info(f"[Leader] Malformed client header: {e}")

            # 读取模型更新（设最大 50MB）
            update_bytes = await stream.receive_some(50 * 1024 * 1024)
            if not update_bytes:
                await stream.close()
                continue

            try:
                state_dict = pickle.loads(update_bytes)
                updates.append(state_dict)
                client_ids.append(client_id)
                logger.info(f"[Leader] Received update from {client_id} (total: {len(updates)})")
            except Exception as e:
                logger.info(f"[Leader] Failed to parse model from {client_id}: {e}")

            await stream.aclose()

            # 可选：如果已收到足够多，可提前结束（比如收到 3 个就停）
            # if len(updates) >= 3:
            #     break

        except Exception as e:
            logger.info(f"[Leader] Error accepting stream: {e}")
            break

    if len(updates) < min_clients:
        logger.info(f"[Leader] Not enough updates (got {len(updates)}, need {min_clients}). Skipping round.")
        return None

    logger.info("[Leader] Aggregating updates...")
    # FedAvg 聚合
    avg_state = {}
    param_keys = updates[0].keys()
    for key in param_keys:
        stacked = torch.stack([update[key].float() for update in updates])
        avg_state[key] = stacked.mean(dim=0)

    logger.info("[Leader] Aggregated")
    model = SimpleCNN()
    model.load_state_dict(avg_state)
    return serialize_model(model)


async def receive_client_updates(cli, round_id: int, timeout: float = 30.0) -> List[dict]:
    """
    Leader 接收来自其他 clients 的模型更新。
    返回 list of state_dict（已 pickle.loads 解析）。
    """
    updates = []
    start_time = trio.current_time()
    logger.info(f"[Leader] Waiting for client updates in round {round_id} (timeout={timeout}s)...")

    while True:
        elapsed = trio.current_time() - start_time
        if elapsed >= timeout:
            logger.info(f"[Leader] Client receive timeout after {len(updates)} updates.")
            break

        remaining = timeout - elapsed
        try:
            # 等待新连接，最多 remaining 秒
            with trio.move_on_after(remaining) as cancel_scope:
                stream = await cli.accept_stream(f"round_{round_id}")

            if cancel_scope.cancelled_caught:
                logger.info("[Leader] No more clients connecting (timeout).")
                break

            # 为单个 client 设置读取超时（比如 10 秒）
            try:
                async with trio.fail_after(10):  # 单个 client 最多 10 秒完成发送
                    # 读取 client ID（可选）
                    cmd_bytes = await stream.receive_some(1024)
                    if cmd_bytes:
                        try:
                            cmd = json.loads(cmd_bytes.decode())
                            client_id = cmd.get("client_id", "unknown")
                        except:
                            client_id = "malformed"
                    else:
                        client_id = "no_id"

                    # 读取模型数据（最大 50MB）
                    model_bytes = await stream.receive_some(50 * 1024 * 1024)
                    if not model_bytes:
                        logger.info(f"[Leader] Empty model from {client_id}")
                    else:
                        state_dict = pickle.loads(model_bytes)
                        updates.append(state_dict)
                        logger.info(f"[Leader] Accepted update from {client_id} (total: {len(updates)})")

            except trio.TooSlowError:
                logger.info(f"[Leader] Client {client_id} took too long to send data.")
            except Exception as e:
                logger.info(f"[Leader] Error processing client {client_id}: {e}")
            finally:
                await stream.aclose()

        except Exception as e:
            logger.info(f"[Leader] Error accepting stream: {e}")
            break

    return updates


# ----------------------------
# Leader 主循环
# ----------------------------
async def start_leader(cli, epoch: int):
    logger.info(f"[Leader] Starting (epoch={epoch})")

    # 初始化 round_0（如果不存在）
    meta_val, _ = await read_var(cli, "global_meta")
    if not meta_val:
        init_model = SimpleCNN()
        init_bytes = serialize_model(init_model)
        await obs_client.put_object("fl-models", "models/round_0.pth", init_bytes)
        meta = {
            "round": 0,
            "revision": 0,
            "model_key": "models/round_0.pth",
            "leader_epoch": epoch
        }
        await write_var(cli, "global_meta", json.dumps(meta), 0)

    current_round = 0

    # Early stopping 配置
    best_val_loss = float('inf')
    patience = int(os.getenv("PATIENCE", "3"))  # 最多容忍多少轮无 improvement
    patience_counter = 0
    max_rounds = int(os.getenv("MAX_ROUNDS", "20"))  # 安全上限，防止无限运行

    while current_round < max_rounds:
        current_round += 1
        logger.info(f"\n[Leader] === Round {current_round}/{max_rounds} ===")

        # 获取上一轮模型
        meta_val, _ = await read_var(cli, "global_meta")
        if not meta_val:
            logger.info("[Leader] No global_meta found. Skipping.")
            break
        meta = json.loads(meta_val)
        model_key = meta["model_key"]
        model_bytes = await obs_client.get_object("fl-models", model_key)
        if not model_bytes:
            logger.info("[Leader] Failed to load model from OBS.")
            break

        # Leader 自训练
        leader_update_bytes = await train_local_model(model_bytes)
        all_updates = [pickle.loads(leader_update_bytes)]

        # 接收 clients
        client_updates = await receive_client_updates(cli, current_round, timeout=30.0)
        all_updates.extend(client_updates)

        logger.info(f"[Leader] Aggregating {len(all_updates)} updates.")

        # FedAvg
        avg_state = {}
        param_keys = all_updates[0].keys()
        for key in param_keys:
            stacked = torch.stack([upd[key].float() for upd in all_updates])
            avg_state[key] = stacked.mean(dim=0)

        # 构建新模型用于评估
        new_model = SimpleCNN()
        new_model.load_state_dict(avg_state)
        new_model.to(torch.device("cuda" if torch.cuda.is_available() else "cpu"))

        # 评估验证损失
        val_loss = evaluate_model(new_model, val_loader)

        # 检查是否 improvement
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            logger.info(f"[Leader] New best validation loss: {val_loss:.4f}")
        else:
            patience_counter += 1
            logger.info(f"[Leader] No improvement. Patience: {patience_counter}/{patience}")

        # 保存模型（无论是否 best，都推进 round）
        new_model_bytes = pickle.dumps(avg_state)
        new_key = f"models/round_{current_round}.pth"
        await obs_client.put_object("fl-models", new_key, new_model_bytes)

        # 更新 global_meta
        new_meta = {
            "round": current_round,
            "revision": current_round,
            "model_key": new_key,
            "leader_epoch": epoch
        }
        await write_var(cli, "global_meta", json.dumps(new_meta), current_round)

        # 检查 early stopping 条件
        if patience_counter >= patience:
            logger.info(f"[Leader] Early stopping triggered after {current_round} rounds.")
            await write_var(cli, "training_finished", "true", 0)
            break

        # 心跳 & sleep
        await publish_heartbeat(cli, "leader")
        await trio.sleep(5)

    logger.info("[Leader] Leader loop exited.")


# ----------------------------
# Client 主循环
# ----------------------------
async def run_as_client(cli, leader_info: Dict[str, Any]):
    leader_id = leader_info["node_id"]
    logger.info(f"[Client] Connecting to leader {leader_id}")

    # 检查训练是否完成
    finished, _ = await read_var(cli, "training_finished")
    if finished == "true":
        logger.info("[Client] Training finished by leader. Exiting.")
        return

    # Step 1: 等待 global_meta（最多 60 秒）
    meta = None
    for _ in range(30):
        meta_val, _ = await read_var(cli, "global_meta")
        if meta_val:
            try:
                meta = json.loads(meta_val)
                break
            except:
                pass
        await trio.sleep(2)
    if not meta:
        logger.info("[Client] Failed to get global_meta after retries")
        return

    round_id = meta["round"] + 1
    model_key = meta["model_key"]

    # Step 2: 下载初始模型
    model_bytes = await obs_client.get_object("fl-models", model_key)
    if not model_bytes:
        logger.info(f"[Client] Model not found: {model_key}")
        return

    # Step 3: 本地训练
    updated_model_bytes = await train_local_model(model_bytes)

    # Step 4: 重试上传（最多 5 次，每次间隔增长）
    for attempt in range(5):
        try:
            logger.info(f"[Client] Attempt {attempt + 1} to upload to round_{round_id}")
            with trio.move_on_after(10) as scope:  # 最多等 10 秒连接
                stream = await cli.open_stream(leader_id, f"round_{round_id}")
            if scope.cancelled_caught:
                raise TimeoutError("Connect timeout")

            await stream.send_all(json.dumps({"client_id": SELF_JOB_ID}).encode())
            await stream.send_all(updated_model_bytes)
            await stream.aclose()
            logger.info(f"[Client] Successfully uploaded update for round {round_id}")
            return

        except Exception as e:
            logger.info(f"[Client] Upload failed (attempt {attempt + 1}): {e}")
            if attempt < 4:
                await trio.sleep(2 ** attempt)  # 指数退避：1, 2, 4, 8 秒
            else:
                logger.info("[Client] Giving up after 5 attempts")


# ----------------------------
# Leader 选举
# ----------------------------
async def try_become_leader(cli) -> bool:
    current_value, current_rev = await read_var(cli, "leader_info")
    if current_value:
        try:
            leader = json.loads(current_value)
            diff = int(time.time()) - leader.get("heartbeat_ts", 0)
            logger.info(
                f"[Leader] Leader {leader['node_id']} is alive, current diff {diff}, and heartbeat timeout is {HEARTBEAT_TIMEOUT}")
            if diff < HEARTBEAT_TIMEOUT:
                return False
        except:
            pass

    new_epoch = current_rev + 1
    claim = {"node_id": SELF_JOB_ID, "epoch": new_epoch, "heartbeat_ts": int(time.time())}
    ok, actual_rev, actual_val = await write_var(cli, "leader_info", json.dumps(claim), new_epoch)

    if ok and actual_rev == (new_epoch + 1):
        return True
    return False


# ----------------------------
# 主循环
# ----------------------------
async def agent_main():
    logger.info(f"FL Agent started: job_id={SELF_JOB_ID}")
    # 初始化验证集
    init_validation_loader()

    async with JobHubClient.connect(JOBHUB_HOST, JOBHUB_PORT, JOBSET_ID, SELF_JOB_ID, SHARED_SECRET) as cli:
        while True:
            await publish_heartbeat(cli)
            if await is_leader_alive(cli):
                logger.info("leader is alive")
                leader_info = await get_leader_info(cli)
                if leader_info and leader_info["node_id"] != SELF_JOB_ID:
                    await run_as_client(cli, leader_info)
                    continue

            logger.info("leader not alive, try become leader")
            if await try_become_leader(cli):
                logger.info("become leader")
                leader_info = await get_leader_info(cli)
                logger.info(f"get leader info success")
                if leader_info and leader_info["node_id"] == SELF_JOB_ID:
                    logger.info("start leader")
                    await start_leader(cli, leader_info["epoch"])
            await trio.sleep(HEARTBEAT_INTERVAL)


if __name__ == "__main__":
    trio.run(agent_main)
