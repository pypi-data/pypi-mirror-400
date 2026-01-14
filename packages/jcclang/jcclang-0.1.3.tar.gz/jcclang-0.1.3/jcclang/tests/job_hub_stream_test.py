import os

import trio

from jcclang.core.jobhub import JobHubClient

host = "127.0.0.1"
port = 7901
# 接口调用需要使用Base64编码：MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIzNDU2Nzg5MDE=
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
            str = await cli.accept_stream("str1")
            print("job1 accepted stream: ", str.name())
            await str.write(b"Hello, it's me, job1!")

            ret = await str.read(1024)
            print("job1 receive: " + ret.decode())
            await str.close()
        except Exception as e:
            print(e)

    print("job1 done")


async def job2():
    async with JobHubClient.connect("127.0.0.1", 7901, "1", "2", shared_secret) as cli:
        try:
            str = await cli.open_stream("1", "str1")
            print("job2 opened stream: ", str.name())
            await str.write(b"Hi, I am job2!")

            ret = await str.read(1024)
            print("job2 receive: " + ret.decode())
            await str.close()
        except Exception as e:
            print(e)
    print("job2 done")


if __name__ == "__main__":
    trio.run(main)
