import os
import traceback

import trio

from jcclang.core.jobhub import JobHubClient, rpc

host = "127.0.0.1"
port = 7901
shared_secret = b"01234567890123456789012345678901"

job_set_id = os.getenv("JOBSET_ID")
job_id = os.getenv("JOB_ID")


async def main():
    async with trio.open_nursery() as nursery:
        nursery.start_soon(job1)
        nursery.start_soon(job2)


async def job1():
    async with JobHubClient.connect("127.0.0.1", 7901, job_set_id, job_id, shared_secret) as cli:
        try:
            req = rpc.VarSet("v1", "1", 0)
            i = 0
            while i < 10:
                resp = await req.do(cli)
                if isinstance(resp, rpc.CodeError):
                    print(resp)
                    return

                if resp.ok:
                    print(f"job1 set to {req.value}, rev: {req.revision}")
                    req.revision = resp.revision
                    req.value = str(int(req.value) + 1)
                    i += 1
                else:
                    print(f"job1 set failed, new: {req.value}, rev: {req.revision}")
                    req.revision = resp.revision
                    req.value = str(int(resp.value) + 1)

        except Exception as e:
            print(e)
            traceback.print_exc()

    print("job1 done")


async def job2():
    async with JobHubClient.connect("127.0.0.1", 7901, "1", "2", shared_secret) as cli:
        try:
            req = rpc.VarSet("v1", "1", 0)
            i = 0
            while i < 10:
                resp = await req.do(cli)
                if isinstance(resp, rpc.CodeError):
                    print(resp)
                    return

                if resp.ok:
                    print(f"job2 set to {req.value}, rev: {req.revision}")
                    req.revision = resp.revision
                    req.value = str(int(req.value) + 1)
                    i += 1
                else:
                    print(f"job2 set failed, new: {req.value}, rev: {req.revision}")
                    req.revision = resp.revision
                    req.value = str(int(resp.value) + 1)

        except Exception as e:
            print(e)
            traceback.print_exc()

    print("job2 done")


if __name__ == "__main__":
    trio.run(main)
