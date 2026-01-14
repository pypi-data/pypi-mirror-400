import trio

from jcclang.api.context import Context
from jcclang.api.jobhub import JobHub
from jcclang.core.jobhub.jobhub import JobHubClient
from jcclang.core.context import *


### START 自动生成的代码，请勿修改 START ###
import fl_client
import fl_server


async def run_user_code(ctx: Context):
    if ctx.job_id() == "0":
        await fl_client.run(ctx)
    elif ctx.job_id() == "1":
        await fl_server.run(ctx)


### END 自动生成的代码，请勿修改 END ###


async def main():

    # todo: jobset_id和job_id不应该放到jobhub的api中，应该是一个全局的参数
    job_set_id = get_jobhub_jobset_id()
    job_id = get_jobhub_job_id()

    async with trio.open_nursery() as nursery:
        async with JobHubClient.connect(
            get_jobhub_addr(),
            get_jobhub_port(),
            job_set_id,
            job_id,
            get_jobhub_secret(),
        ) as cli:
            job_hub = JobHub(cli)
            ctx = Context(nursery, job_set_id, job_id, job_hub)
            await run_user_code(ctx)


if __name__ == "__main__":
    trio.run(main)
