# 移除asyncio导入，因为使用trio
import json
import os
import random
from typing import List, Dict, Any

import trio

from jcclang.examples.fl_3.const import INITIAL_MODEL_FROM_CLIENT, FL_CONFIG, \
    DATA_OWNER
from jcclang.examples.fl_3.model import serialize_model
from jcclang.examples.fl_3.utils import write_var, read_var, logger, publish_heartbeat, get_leader_info, \
    write_stream

# ----------------------------
# 配置常量
# ----------------------------
LOCAL_DATA_ROOT = "./client_data"  # 数据块存储根目录
MODEL_WAIT_TIMEOUT = 300  # 最大等待模型时间（秒）
CANDIDATE = "candidate"


# ----------------------------
# 全局状态（Client 内存中）
# ----------------------------
class ClientState:
    def __init__(self):
        self.current_ownership_version: str = ""
        self.owned_blocks: List[str] = []
        self.train_loader = None
        self.num_samples: int = 0
        self.model = None
        self.fl_config: Dict = {}
        self.data_metadata: Dict[str, Dict] = {}


# ----------------------------
# 数据加载工具（需用户实现）
# ----------------------------
def load_data_from_blocks(data_info: List) -> tuple[Any, int]:
    """
    根据 block_id 列表加载 Dataset 和 DataLoader
    返回 (train_loader, total_num_samples)
    """
    from torch.utils.data import DataLoader, ConcatDataset
    datasets = []
    total_samples = 0

    for info in data_info:
        path = info.get("path")
        # 判断这个路径存不存在
        if not os.path.exists(path):
            logger.info(f"[Client] Warning: Block {info} not found")
            continue

        # 遍历path下的所有文件
        for file_name in os.listdir(path):
            # 拼接完整路径
            file_path = os.path.join(path, file_name)
            logger.info(f"[Client] Loading data from {file_path}")
            dataset = create_dataset_from_path(file_path, "mnist")
            datasets.append(dataset)
        # total_samples += metadata[bid]["size"]

    if not datasets:
        raise ValueError("No valid data blocks loaded!")

    combined_dataset = ConcatDataset(datasets)
    loader = DataLoader(combined_dataset, batch_size=32, shuffle=True)
    return loader, total_samples


def create_dataset_from_path(path: str, data_type: str):
    """
    根据数据类型创建 Dataset
    """
    if data_type == "mnist":
        from torch.utils.data import TensorDataset
        import pickle
        with open(path, "rb") as f:
            data = pickle.load(f)

        dataset = TensorDataset(data['images'], data['labels'])
        return dataset
    elif data_type == "image":
        from torchvision.datasets import ImageFolder
        return ImageFolder(path)
    elif data_type == "tabular":
        # 自定义 CSV/TensorDataset 加载
        import torch
        data = torch.load(os.path.join(path, "data.pt"))
        labels = torch.load(os.path.join(path, "labels.pt"))
        from torch.utils.data import TensorDataset
        return TensorDataset(data, labels)
    else:
        raise NotImplementedError(f"Unsupported data type: {data_type}")


# ----------------------------
# 模型工具
# ----------------------------
def create_model(config: Dict):
    """根据配置创建模型（与 Leader 一致）"""
    from model import SimpleCNN
    model = SimpleCNN()
    return model


def train_model(model, train_loader, config: Dict):
    """执行本地训练"""
    import torch
    import torch.optim as optim
    import torch.nn as nn

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    model.train()

    optimizer = optim.SGD(model.parameters(), lr=config["learning_rate"])
    criterion = nn.CrossEntropyLoss()

    for epoch in range(config["local_epochs"]):
        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(device), target.to(device)
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()

    return model.cpu()


# def serialize_model(model) -> bytes:
#     import torch
#     from io import BytesIO
#     buffer = BytesIO()
#     torch.save(model.state_dict(), buffer)
#     return buffer.getvalue()


# ----------------------------
# 主 Client 逻辑
# ----------------------------
async def monitor_leader_and_send_model(jobhub_cli, job_id: str, state: ClientState):
    """
    监控leader_id，如果当前client成为leader，则发送最新模型作为初始模型
    """
    while True:
        # 读取leader_info来获取当前的leader_id
        init_model_from_client, _ = await read_var(jobhub_cli, INITIAL_MODEL_FROM_CLIENT)
        try:
            if init_model_from_client and init_model_from_client != "":
                logger.info(f"[Client] Received initial model from leader: {init_model_from_client}")
                leader_info = json.loads(init_model_from_client)
                client_id = leader_info.get("client_id")
                leader_id = leader_info.get("leader_id")

                # 检查当前client是否是leader
                if client_id == job_id:
                    logger.info(
                        f"[Client] This client is now the leader (leader_id={client_id}). Checking if we need to send initial model...")

                    # 检查是否有最新模型
                    if hasattr(state, 'model') and state.model is not None:
                        # 序列化最新模型
                        model_bytes = serialize_model(state.model)

                        # 发送初始模型到指定的流
                        # stream_name = f"initial_model_from_{job_id}"
                        logger.info(
                            f"[Client] Sending latest model as initial model to stream: {INITIAL_MODEL_FROM_CLIENT}")

                        # 清空变量，表示不用再初始化
                        await write_var(jobhub_cli, INITIAL_MODEL_FROM_CLIENT, "", 0)

                        # 使用write_stream发送模型
                        # 这里不需要指定目标job_id，因为这是一个用于接收的流名称
                        await write_stream(jobhub_cli, leader_id, INITIAL_MODEL_FROM_CLIENT, model_bytes)
                        logger.info(f"[Client] Successfully sent initial model (size: {len(model_bytes)} bytes)")
                    else:
                        logger.info(f"[Client] No trained model available to send as initial model")
        except Exception as e:
            # 如果失败了，恢复初始化信息
            await write_var(jobhub_cli, INITIAL_MODEL_FROM_CLIENT, init_model_from_client, 0)
            logger.error(f"[Client] Error in monitor_leader_and_send_model: {e}")

        # 每5秒检查一次，与心跳间隔保持一致
        await trio.sleep(5.0)


async def run_as_client(jobhub_cli, job_id: str):
    async with trio.open_nursery() as nursery:
        # 创建客户端状态对象，用于共享给监控任务
        client_state = ClientState()

        # 启动独立的心跳任务
        nursery.start_soon(publish_heartbeat, jobhub_cli, CANDIDATE, job_id, 5.0)

        # 启动leader监控任务
        nursery.start_soon(monitor_leader_and_send_model, jobhub_cli, job_id, client_state)

        # 启动主客户端逻辑
        await start_client(jobhub_cli, job_id, client_state)


async def start_client(jobhub_cli, job_id: str, client_state: ClientState):
    import torch
    """
    启动联邦学习客户端（使用 JobHub Stream 传输模型）
    """
    state = client_state

    logger.info(f"[Client] [{job_id}] Starting client...")

    # Step 1: 获取全局配置（KV）
    logger.info("[Client] Waiting for fl_config...")
    config_val, _ = await read_var(jobhub_cli, FL_CONFIG)
    state.fl_config = json.loads(config_val)
    logger.info(f"[Client] Config loaded: {state.fl_config}")

    # Step 2: 获取初始数据归属（KV）
    # logger.info("[Client] Fetching initial data ownership...")
    # version_val, _ = await read_var(jobhub_cli, DATA_OWNERSHIP_VERSION)
    # state.current_ownership_version = version_val

    # ownership_payload, _ = await read_var(jobhub_cli, f"data_ownership_v{version_val}")
    # payload = json.loads(ownership_payload)
    # state.data_metadata = payload["metadata"]

    client_owner = DATA_OWNER + job_id
    source_str, _ = await read_var(jobhub_cli, client_owner)
    state.owned_blocks = json.loads(source_str).get('ownership')
    # state.owned_blocks = payload["ownership"].get(job_id, [])
    if not state.owned_blocks:
        logger.info("[Client] No data assigned! Exiting.")
        return

    # Step 3: 加载本地数据
    logger.info(f"[Client] Loading data blocks: {state.owned_blocks}")
    state.train_loader, state.num_samples = load_data_from_blocks(
        state.owned_blocks
    )
    logger.info(f"[Client] Loaded {state.num_samples} samples.")

    # Step 4: 上报元信息（KV）
    # meta = {
    #     "job_id": job_id,
    #     "num_samples": state.num_samples,
    #     "data_blocks": state.owned_blocks,
    #     "device": "gpu" if torch.cuda.is_available() else "cpu"
    # }
    # await write_var(jobhub_cli, f"client_meta_{job_id}", json.dumps(meta), 0)
    # logger.info("[Client] Meta info reported.")

    # Step 5: 训练主循环
    round_count = 0
    while True:
        # 检查是否训练结束（KV）
        try:
            finished, _ = await read_var(jobhub_cli, "training_finished")
            if finished == "true":
                logger.info("[Client] Training finished signal received. Exiting.")
                break
        except Exception as e:
            pass

        # 每轮迭代需检查数据块是否更新
        source_str, _ = await read_var(jobhub_cli, client_owner)
        new_blocks = json.loads(source_str).get('ownership')

        if new_blocks != state.owned_blocks:
            state.owned_blocks = new_blocks
            if state.owned_blocks:
                state.train_loader, state.num_samples = load_data_from_blocks(
                    state.owned_blocks
                )
                logger.info(f"[Client] Reloaded data: {state.num_samples} samples.")
            else:
                logger.info("[Client] No data assigned after reload. Waiting...")
                state.train_loader = None
                state.num_samples = 0

        if not state.owned_blocks or state.train_loader is None:
            logger.info("[Client] No data assigned. Waiting...")
            await trio.sleep(5)
            continue

        round_count += 1
        logger.info(f"[Client] \n--- Client round {round_count} ---")

        # ==============================
        # 接收模型（使用 STREAM）
        # ==============================
        try:
            # 等待 Leader 发起的流连接，添加超时控制
            stream_name = f"model_to_{job_id}"
            logger.info(f"[Client] Round {round_count}, waiting for model stream, stream name: {stream_name}")

            stream_in = await jobhub_cli.accept_stream(stream_name)

            model_bytes = await stream_in.read()
            logger.info(f"[Client] Received {len(model_bytes)} bytes from stream.")

            await stream_in.close()
            logger.info(f"[Client] Received model via stream (size: {len(model_bytes)} bytes).")
        except Exception as e:
            logger.info(f"[Client] Error receiving model stream: {e}")
            continue

        # 检查是否收到了有效的模型数据
        if 'model_bytes' not in locals() or not model_bytes:
            logger.info("[Client] No valid model data received. Skipping round.")
            continue

        # 初始化或更新模型
        state.model = create_model(state.fl_config)
        from io import BytesIO
        buffer = BytesIO(model_bytes)
        state.model.load_state_dict(torch.load(buffer, map_location='cpu'))

        # 执行本地训练
        logger.info("[Client] Starting local training...")
        # trained_model = train_model(state.model, state.train_loader, state.fl_config)
        # trained_model = await trio.to_thread.run_sync(train_model, state.model, state.train_loader, state.fl_config)
        # logger.info("[Client] Local training completed.")

        # ==============================
        # 发送模型（使用 STREAM）
        # ==============================
        # 随机睡眠3-6s
        await trio.sleep(10 + random.random() * 3)
        result_bytes = serialize_model(state.model)
        # result_bytes = serialize_model(trained_model)
        logger.info(f"[Client] Model size: {len(result_bytes)} bytes.")
        sent_success = False

        for i in range(3):
            logger.info(f"[Client] Trying to send model to leader, attempt {i + 1}...")

            try:
                # 快速检查leader是否存在
                info = await get_leader_info(jobhub_cli)

                if not info:
                    logger.error("[Client] Leader does not exist, waiting...")
                    await trio.sleep(2)
                    continue

                leader_job_id = info['node_id']

                # 发送模型前，查询leader round,用于调试
                leader_round, _ = await read_var(jobhub_cli, "leader_round")

                logger.info(
                    f"[Client] Round {round_count}, sending model to leader: {leader_job_id}, leader round: {leader_round}")

                # 睡眠3s，等待leader接收
                await trio.sleep(3)

                ok = await write_stream(jobhub_cli, leader_job_id, f"model_from_{job_id}", result_bytes)

                if ok:
                    logger.info("[Client] Updated model uploaded via stream.")
                    sent_success = True
                    break

                logger.info(f"[Client] Failed to send model to leader, retrying...")

            except Exception as e:
                logger.info(f"[Client] Failed to send model to leader: {e}")

            # 指数退避重试
            await trio.sleep(2 ** i)

        if not sent_success:
            logger.warning(f"[Client] Failed to send model to leader after 3 attempts, continuing...")

        # 上报性能指标（KV）
        perf = {
            "round": round_count,
            "num_samples": state.num_samples,
            # "device": meta["device"]
        }
        try:
            logger.info(f"[Client] Reporting performance: {perf}")
            await write_var(jobhub_cli, f"perf_{job_id}", json.dumps(perf), 0)
        except Exception as e:
            logger.info(f"[Client] Failed to report perf: {e}")

    logger.info(f"[Client] [{job_id}] Client shutdown complete.")
