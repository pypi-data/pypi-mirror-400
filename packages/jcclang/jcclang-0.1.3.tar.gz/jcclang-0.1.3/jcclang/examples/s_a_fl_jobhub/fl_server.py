# server.py
"""
Server 端脚本（用 JobHubAPI 与各 client 进行通信）
使用方式（简单）：
  python server.py

注意：
  - 在不同机器上运行 client.py 时，把 CLIENT_IDS 列表与 client 启动时的 JOB_ID 保持一致
  - 请确保 jobhub_api.jobhub_instance() 的 host/port/secret 配置正确
"""

import io
import os
from contextlib import aclosing
from typing import List

from jcclang.api.context import Context
import torch
import trio


from jcclang.examples.semi_asychronous_fl.fl_client import (
    SmallCNN,
)  # model 定义


# ---------------------------
# 全局配置（可按需修改或从 env 读取）
# ---------------------------
os.environ["JOBHUB_ADDR"] = "127.0.0.1"
os.environ["JOBHUB_PORT"] = "7901"
os.environ["JOBHUB_JOBSET_ID"] = "1"
os.environ["JOBHUB_JOB_ID"] = "1"
os.environ["JOBHUB_SECRET"] = "01234567890123456789012345678901"
# JOBHUB_GROUP = "1"
# SERVER_JOB_ID = "server"  # server 在 JobHub 上的 job id
CLIENT_IDS = [
    "client-0",
    "client-1",
    "client-2",
    "client-3",
]  # 对应每台 client 的 job id
# NUM_CLIENTS = len(CLIENT_IDS)

ROUNDS = 10
LOCAL_EPOCHS = 1
C_PARAM = 0.6
M_PARAM = 0.5
TAU_MAX = 5
SIGMA_MAX = 3
L_THRESHOLD = 2.0
SINKHORN_EPS = 0.1

MODEL_NAME = "global_model"  # var 名称（用于发布模型版本等）


# ---------------------------
# 辅助函数：序列化/反序列化 state_dict
# ---------------------------
def serialize_state_dict(state_dict: dict) -> bytes:
    buf = io.BytesIO()
    torch.save(state_dict, buf)
    return buf.getvalue()


def deserialize_state_dict(b: bytes):
    buf = io.BytesIO(b)
    return torch.load(buf)


# ---------------------------
# Server 类（简化版，按轮次发布模型/收集更新）
# ---------------------------
class FLServer:
    def __init__(self, ctx: Context, client_ids: List[str]):
        self.ctx = ctx
        self.client_ids = client_ids
        self.num_clients = len(client_ids)
        self.global_model = SmallCNN(num_classes=10)
        # 每轮的状态统计
        self.P_counts = {cid: 0 for cid in client_ids}
        self.v = {cid: 0 for cid in client_ids}  # staleness
        # jobhub api
        self.api = None

    async def send_model_to_client(
        self, dst_job_id: str, state_dict: dict, name: str = "model"
    ):
        b = serialize_state_dict(state_dict)
        stream = await self.ctx.job_hub().open_stream(dst_job_id, name=name)
        try:
            await stream.write(b)
        finally:
            await stream.close()

    async def receive_update_from_client(
        self, accept_name: str = "update", timeout: int = 10
    ):
        with trio.move_on_after(timeout):
            stream = await self.ctx.job_hub().accept_stream(accept_name)
            raw = await stream.read(1 << 30)
            try:
                payload = torch.load(io.BytesIO(raw))
                cid = payload.get("cid")
                state = payload.get("state_dict")
                local_loss = payload.get("local_loss")
                phi = payload.get("phi", 1)
                return cid, state, local_loss, phi
            except Exception as e:
                print(f"[Server] failed to parse update payload: {e}")
                return None

            finally:
                await stream.close()

        print(f"[Server] timeout waiting for update on {accept_name}")
        return None

    async def run_round(self, round_idx: int):
        print(f"[Server] start round {round_idx}")
        selected = self.client_ids  # Select all clients (or sample based on C_PARAM)
        state_cpu = {k: v.cpu() for k, v in self.global_model.state_dict().items()}

        # Send model to all selected clients concurrently
        async with trio.open_nursery() as nursery:
            for cid in selected:
                nursery.start_soon(self.send_model_to_client, cid, state_cpu, "model")

        # Collect updates with a deadline
        collected = []
        async with trio.open_nursery() as nursery:
            collect_deadline = trio.current_time() + 5.0  # 5-second window
            for cid in selected:
                # Start a task to receive update from each client with a timeout
                nursery.start_soon(
                    self._receive_with_timeout,
                    cid,
                    "update",
                    collect_deadline,
                    collected,
                )

            # Wait until deadline or all updates are collected
            while nursery.child_tasks and trio.current_time() < collect_deadline:
                await trio.sleep(0.1)

        if not collected:
            print("[Server] no updates collected this round")
            return

        # Aggregate updates
        new_state = {
            k: torch.zeros_like(v) for k, v in self.global_model.state_dict().items()
        }
        for cid, st, local_loss, phi in collected:
            for k in new_state.keys():
                new_state[k] += st[k]
            self.P_counts[cid] = self.P_counts.get(cid, 0) + 1
            self.v[cid] = 0
        num = len(collected)
        for k in new_state.keys():
            new_state[k] = new_state[k] / num
        self.global_model.load_state_dict(new_state)
        print(f"[Server] aggregated {len(collected)} updates")

    async def _receive_with_timeout(
        self, cid: str, accept_name: str, deadline: float, collected: list
    ):
        """Helper to receive updates with a deadline"""
        with trio.move_on_at(deadline):
            try:
                res = await self.receive_update_from_client(accept_name)
                if res and res[0] == cid:
                    collected.append(res)
            except Exception as e:
                print(f"[Server] failed to receive update from {cid}: {e}")

    async def run(self, rounds: int = ROUNDS):
        last_round_var = await self.ctx.job_hub().get_var("server:last_round")

        for r in range(1, rounds + 1):
            await self.run_round(r)
            # 可选：把一些监控信息写到 jobhub 全局变量
            await last_round_var.set(str(r))
            # 小睡片刻
            await trio.sleep(0.1)


# ---------------------------
# CLI 入口
# ---------------------------
<<<<<<< Updated upstream
=======
<<<<<<< HEAD
def run_as_main():
    async def _main():
        async with aclosing(jobhub_instance()) as api:
            server = FLServer(CLIENT_IDS)
            server.api = await api  # Assign the API instance
            await server.run(ROUNDS)
>>>>>>> Stashed changes

async def run(ctx: Context):
    server = FLServer(ctx, CLIENT_IDS)
    await server.run(ROUNDS)

<<<<<<< Updated upstream
=======

if __name__ == "__main__":
    run_as_main()
=======
async def run(ctx: Context):
    server = FLServer(ctx, CLIENT_IDS)
    await server.run(ROUNDS)
>>>>>>> fdd5b21693a47286e7c3f05f3355ef10b90f5826
>>>>>>> Stashed changes
