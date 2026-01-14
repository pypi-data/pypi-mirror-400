# client.py
"""
Client 端脚本（每台 client 主机运行）
用法（命令行）：
  CLIENT_JOB_ID=client-0 python client.py

脚本会：
 - 连接 JobHub（jobhub_instance）
 - 被动等待 server 的 model 流（accept_stream(name="model")）
 - 接收 model、反序列化并执行本地训练（SmallCNN）
 - 将本地更新通过 open_stream(dst_job_id=SERVER_JOB_ID, name="update") 发回 server
"""

import io
import os
import random

from jcclang.api.context import Context
import torch
import torch.nn as nn
import torchvision
import torchvision.transforms as transforms
import trio
from torch.utils.data import Subset, DataLoader

from jcclang.examples.semi_asychronous_fl.fl_client import (
    SmallCNN,
)  # model 定义

# ---------------------------
# 全局配置（可按需从环境变量读取）
# ---------------------------
os.environ["JOBHUB_ADDR"] = "127.0.0.1"
os.environ["JOBHUB_PORT"] = "7901"
os.environ["JOBHUB_JOBSET_ID"] = "1"
os.environ["JOBHUB_JOB_ID"] = "2"
os.environ["JOBHUB_SECRET"] = "01234567890123456789012345678901"

SERVER_JOB_ID = os.environ.get("SERVER_JOB_ID", "server")
CLIENT_JOB_ID = os.environ.get("CLIENT_JOB_ID", "client-0")

DATA_ROOT = os.environ.get("DATA_ROOT", "D:\\Model\\dataset\\fashion_mnist")
BATCH_SIZE = 64
LOCAL_EPOCHS = 1
LR = 0.01


# ---------------------------
# 辅助：反序列化 state
# ---------------------------
def deserialize_state_dict(b: bytes):
    buf = io.BytesIO(b)
    return torch.load(buf)


def serialize_update_payload(cid, state_dict, local_loss, phi=1):
    buf = io.BytesIO()
    payload = {
        "cid": cid,
        "state_dict": state_dict,
        "local_loss": local_loss,
        "phi": phi,
    }
    torch.save(payload, buf)
    return buf.getvalue()


# ---------------------------
# 本地训练函数
# ---------------------------
def local_train_from_state(
    state_dict,
    train_indices,
    val_indices,
    data_root=DATA_ROOT,
    local_epochs=1,
    lr=0.01,
    device="cpu",
):
    transform = transforms.Compose([transforms.ToTensor()])
    full_train = torchvision.datasets.FashionMNIST(
        root=data_root, train=True, download=False, transform=transform
    )
    train_subset = (
        Subset(full_train, train_indices)
        if len(train_indices) > 0
        else Subset(full_train, [0])
    )
    val_subset = (
        Subset(full_train, val_indices)
        if len(val_indices) > 0
        else Subset(full_train, [0])
    )
    train_loader = DataLoader(train_subset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_subset, batch_size=BATCH_SIZE, shuffle=False)

    device_t = torch.device(device)
    model = SmallCNN(num_classes=10).to(device_t)
    model.load_state_dict(state_dict)
    model.train()
    opt = torch.optim.SGD(model.parameters(), lr=lr)
    loss_fn = nn.CrossEntropyLoss()
    for ep in range(local_epochs):
        for xb, yb in train_loader:
            xb = xb.to(device_t)
            yb = yb.to(device_t)
            opt.zero_grad()
            out = model(xb)
            loss = loss_fn(out, yb)
            loss.backward()
            opt.step()
    # 估计本地val loss
    model.eval()
    total = 0.0
    cnt = 0
    with torch.no_grad():
        for xb, yb in val_loader:
            xb = xb.to(device_t)
            yb = yb.to(device_t)
            out = model(xb)
            total += float(loss_fn(out, yb).item()) * xb.size(0)
            cnt += xb.size(0)
            if cnt >= 200:
                break
    avg_loss = total / max(1, cnt)
    return {k: v.cpu() for k, v in model.state_dict().items()}, avg_loss


# ---------------------------
# Client 主逻辑
# ---------------------------
class FLClient:
    def __init__(self, job_id: str, server_id: str, train_indices, val_indices):
        self.job_id = job_id
        self.server_id = server_id
        self.train_indices = train_indices
        self.val_indices = val_indices
        self.api = None

    async def accept_and_train_loop(self, ctx: Context):
        """
        永久循环：
         - accept_stream(name="model") 接收 server 推送的全局模型（blocking）
         - 反序列化、训练 local_epochs
         - open_stream(dst=SERVER_JOB_ID, name="update") 发送更新（state_dict + metadata）
        """
        print(f"[Client {self.job_id}] entering accept loop")
        while True:
            try:
                stream = await ctx.job_hub().accept_stream("model")
                print(f"[Client {self.job_id}] accepted model stream: {stream.name()}")
                raw = await stream.read(1 << 30)  # 一次性读取全部
                await stream.close()
                state = deserialize_state_dict(raw)
                # local train
                local_state, local_loss = local_train_from_state(
                    state,
                    self.train_indices,
                    self.val_indices,
                    data_root=DATA_ROOT,
                    local_epochs=LOCAL_EPOCHS,
                    lr=LR,
                )
                # 组装 payload 并发送回 server
                payload_bytes = serialize_update_payload(
                    self.job_id, local_state, local_loss, phi=1
                )
                up_stream = await ctx.job_hub().open_stream(self.server_id, name="update")
                await up_stream.write(payload_bytes)
                await up_stream.close()
                print(f"[Client {self.job_id}] sent update (loss={local_loss:.4f})")
            except Exception as e:
                print(f"[Client {self.job_id}] exception in accept loop: {e}")
                # 重连会在 jobhub_api 内自动处理；这里 sleep 后重试
                await trio.sleep(2)


# ---------------------------
# CLI 入口：从环境或命令行参数读取 job id，并构建 fake indices（示例）
# ---------------------------
async def run(ctx: Context):
    # 这里为了示例简单，把数据划分策略改为随机 subset（真实部署每台机器有自己的数据）
    # 你应该在每台 client 上准备好 train_indices / val_indices 的文件或固定划分
    # 下面生成随机 indices 供 demo 使用（仅当实际数据存在相应索引）
    total_samples = 60000  # FashionMNIST train size
    all_idx = list(range(total_samples))
    random.shuffle(all_idx)
    # 每个 client 取 6000 样本，val 10%
    size_per_client = max(1, total_samples // 10)
    start = 0
    # 在真实场景中，client 程序应读取本机的索引文件；本示例只是演示
    client_train_idx = all_idx[start : start + size_per_client]
    client_val_idx = client_train_idx[: max(1, len(client_train_idx) // 10)]
    client = FLClient(CLIENT_JOB_ID, SERVER_JOB_ID, client_train_idx, client_val_idx)

    await client.accept_and_train_loop(ctx)
