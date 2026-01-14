import os

import trio

from jcclang.core.jobhub import JobHubClient
from jcclang.examples.fl_3.client import run_as_client
from jcclang.examples.fl_3.leader import run_as_leader
from jcclang.examples.fl_3.model import SimpleCNN
from jcclang.examples.fl_3.utils import logger, is_leader_alive, try_become_leader, is_client_alive

JOBHUB_HOST = os.getenv("JOBHUB_HOST", "127.0.0.1")
JOBHUB_PORT = int(os.getenv("JOBHUB_PORT", "7901"))
SHARED_SECRET = os.getenv("JOBHUB_SECRET", "01234567890123456789012345678901").encode()

JOBSET_ID = os.getenv("JOBSET_ID", "fl_mnist")
SELF_JOB_ID = os.getenv("JOB_ID", "client_0")
LEADER_JOB_ID = "leader_" + SELF_JOB_ID

CLIENT_DATA_DIR = os.getenv("CLIENT_DATA_DIR", "./client_data")

HEARTBEAT_INTERVAL = 5
HEARTBEAT_TIMEOUT = 15

cnn_model = SimpleCNN()


async def leader_thread():
    async with JobHubClient.connect(JOBHUB_HOST, JOBHUB_PORT, JOBSET_ID, LEADER_JOB_ID, SHARED_SECRET) as cli:
        while True:
            if not await is_leader_alive(cli) and await try_become_leader(cli=cli, job_id=LEADER_JOB_ID):
                logger.info("leader not alive, try become leader")
                finished = await run_as_leader(job_id=LEADER_JOB_ID, jobhub_cli=cli, scheduler=None,
                                               model_template=cnn_model,
                                               initial_config_path="./initial_ownership.json",
                                               checkpoint_path="./checkpoint")
                if finished:
                    logger.info("leader finished")
                    return

            await trio.sleep(HEARTBEAT_INTERVAL)


async def client_thread():
    async with JobHubClient.connect(JOBHUB_HOST, JOBHUB_PORT, JOBSET_ID, SELF_JOB_ID, SHARED_SECRET) as cli:
        while True:
            if await is_leader_alive(cli) and not await is_client_alive(cli, SELF_JOB_ID):
                logger.info("client is not alive, try become client")
                await run_as_client(cli, SELF_JOB_ID)

            await trio.sleep(HEARTBEAT_INTERVAL)


async def agent_main():
    logger.info(f"FL Agent started: job_id={SELF_JOB_ID}")

    # async with JobHubClient.connect(JOBHUB_HOST, JOBHUB_PORT, JOBSET_ID, SELF_JOB_ID, SHARED_SECRET) as cli:
    async with trio.open_nursery() as nursery:
        nursery.start_soon(leader_thread)
        # nursery.start_soon(client_thread)


if __name__ == "__main__":
    trio.run(agent_main)
