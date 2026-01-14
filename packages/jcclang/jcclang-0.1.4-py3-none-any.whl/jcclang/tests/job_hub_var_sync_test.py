import json
import logging
import os
import time
from typing import Optional, Tuple

import trio

from jcclang.core.jobhub import JobHubClient, rpc

JOBHUB_HOST = os.getenv("JOBHUB_HOST", "127.0.0.1")
JOBHUB_PORT = int(os.getenv("JOBHUB_PORT", "7901"))
SHARED_SECRET = os.getenv("JOBHUB_SECRET", "01234567890123456789012345678901").encode()

JOBSET_ID = os.getenv("JOBSET_ID", "fl_mnist")
SELF_JOB_ID = os.getenv("JOB_ID", "client_1")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


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
    # logger.info(f"[VarSet] OK: {resp}")
    return resp.ok, resp.revision, resp.value


async def publish_heartbeat(cli, role: str = "candidate"):
    ts = int(time.time())
    logger.info(f"[Heartbeat] Publishing {role} heartbeat")
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


async def heartbeat_task(cli, role: str, interval: float = 5.0):
    """后台任务：定期发送心跳"""
    while True:
        try:
            await publish_heartbeat(cli, role)
        except Exception as e:
            logger.exception(f"[Heartbeat] Error: {e}")
        await trio.sleep(interval)


async def agent_main():
    async with JobHubClient.connect(JOBHUB_HOST, JOBHUB_PORT, JOBSET_ID, SELF_JOB_ID, SHARED_SECRET) as cli:
        claim = {"node_id": SELF_JOB_ID, "epoch": 1, "heartbeat_ts": int(time.time())}
        ok, actual_rev, actual_val = await write_var(cli, "leader_info", json.dumps(claim), 1)

        async with trio.open_nursery() as nursery:
            # 启动独立的心跳任务
            nursery.start_soon(heartbeat_task, cli, "leader", 2)
            while True:
                await publish_heartbeat(cli)
                await trio.sleep(2)


if __name__ == "__main__":
    trio.run(agent_main)
