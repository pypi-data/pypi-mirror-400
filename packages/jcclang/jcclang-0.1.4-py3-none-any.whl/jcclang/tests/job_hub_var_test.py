import logging
import socket
import os
import traceback
from noise.connection import NoiseConnection, Keypair
from argon2.low_level import hash_secret_raw, Type
from struct import pack
import trio

from jcclang.core.jobhub import JobHubClient, rpc

host = "127.0.0.1"
port = 7901
shared_secret = b"01234567890123456789012345678901"


async def main():
    async with trio.open_nursery() as nursery:
        nursery.start_soon(job1)
        nursery.start_soon(job2)


async def job1():
    async with JobHubClient.connect("127.0.0.1", 7901, "1", "1", shared_secret) as cli:
        try:
            req = rpc.VarWatch("v1")
            resp = await req.do(cli)
            if isinstance(resp, rpc.CodeError):
                print(resp)
                return

            while True:
                evt = await req.next()
                if evt is None:
                    break
                print(f"{evt.value}@{evt.revision}")
                if evt.value == "done":
                    break
            await req.close()

        except Exception as e:
            print(e)
            traceback.print_exc()

    print("job1 done")


async def job2():
    async with JobHubClient.connect("127.0.0.1", 7901, "1", "2", shared_secret) as cli:
        try:
            await trio.sleep(3)
            req = rpc.VarSet("v1", "hello")
            resp = await req.do(cli)
            if isinstance(resp, rpc.CodeError):
                print(resp)
                return

            await trio.sleep(1)

            req.value = "world"
            resp = await req.do(cli)
            if isinstance(resp, rpc.CodeError):
                print(resp)
                return

            await trio.sleep(1)

            req.value = "foo"
            resp = await req.do(cli)
            if isinstance(resp, rpc.CodeError):
                print(resp)
                return

            await trio.sleep(1)

            req.value = "bar"
            resp = await req.do(cli)
            if isinstance(resp, rpc.CodeError):
                print(resp)
                return

            req.value = "done"
            resp = await req.do(cli)
            if isinstance(resp, rpc.CodeError):
                print(resp)
                return

        except Exception as e:
            print(e)
            traceback.print_exc()

    print("job2 done")


if __name__ == "__main__":
    trio.run(main)
