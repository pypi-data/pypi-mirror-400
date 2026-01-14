import os
import time

import trio

os.environ["JOBHUB_ADDR"] = "127.0.0.1"
os.environ["JOBHUB_PORT"] = "7901"
os.environ["JOBHUB_JOBSET_ID"] = "1"
os.environ["JOBHUB_JOB_ID"] = "1"
os.environ["JOBHUB_SECRET"] = "01234567890123456789012345678901"

from jcclang.api.jobhub_api2 import JobHubManager


async def worker():
    async with JobHubManager(client_id="2222") as mgr:
        revision = 0
        value = "1"
        name = time.time()
        for _ in range(10):
            resp = await mgr.var_set("v1", value, revision)
            if resp.ok:
                print(f"{name} set {value}@{revision}")
                revision = resp.revision
                value = str(int(value) + 1)
            else:
                print(f"{name} set failed, updating...")
                revision = resp.revision
                value = str(int(resp.value) + 1)
        print(f"{name} done")


async def worker2():
    async with JobHubManager(client_id="111") as mgr:
        revision = 0
        value = "1"
        name = time.time()
        for _ in range(10):
            resp = await mgr.var_set("v1", value, revision)
            if resp.ok:
                print(f"{name} set {value}@{revision}")
                revision = resp.revision
                value = str(int(value) + 1)
            else:
                print(f"{name} set failed, updating...")
                revision = resp.revision
                value = str(int(resp.value) + 1)
        print(f"{name} done")


async def main():
    async with trio.open_nursery() as nursery:
        nursery.start_soon(worker)
        nursery.start_soon(worker2)


if __name__ == '__main__':
    trio.run(main)
