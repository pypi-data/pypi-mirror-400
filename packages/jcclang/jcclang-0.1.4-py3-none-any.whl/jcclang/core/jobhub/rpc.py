import json
from dataclasses import dataclass

from dacite import from_dict

from .jobhub import JobHubClient
from .types import CodeError
from ..io.chunked import ChunkedReader


@dataclass
class VarGetResp:
    value: str
    revision: int


@dataclass
class VarGet:
    name: str

    async def do(self, cli: JobHubClient) -> VarGetResp | CodeError:
        resp = await unary_rpc(cli, "/var/get", json.dumps(self.__dict__).encode())
        if isinstance(resp, CodeError):
            return resp
        data = json.loads(resp)
        return from_dict(VarGetResp, data)


@dataclass
class VarSetResp:
    ok: bool
    revision: int
    # 仅在 ok 为 False 时不为空
    value: str


@dataclass
class VarSet:
    name: str
    value: str
    revision: int | None = None

    async def do(self, cli: JobHubClient) -> VarSetResp | CodeError:
        data = json.dumps(self.__dict__).encode()
        resp = await unary_rpc(cli, "/var/set", data)
        if isinstance(resp, CodeError):
            return resp
        data = json.loads(resp)
        return from_dict(VarSetResp, data)


@dataclass
class VarWatchEvent:
    value: str
    revision: int


class VarWatch:
    def __init__(self, name: str):
        self.name = name
        self._cr: ChunkedReader | None = None

    async def do(self, cli: JobHubClient) -> CodeError | None:
        data = json.dumps(self.__dict__).encode()
        cw, rr = await cli.do_rpc("/var/watch")
        try:
            await cw.write_data_part("", data)
            await cw.send_eof()

            resp = await rr.get()
            if isinstance(resp, CodeError):
                return resp

            self._cr = resp
            return None

        except:
            await rr.close()
            raise
        finally:
            await cw.close()

    async def next(self) -> VarWatchEvent | None:
        if self._cr is None:
            raise ValueError("WatchVarChan not initialized")

        part = await self._cr.next_data_part()
        if part is None:
            return None
        _, data = part
        data = json.loads(data)
        return from_dict(VarWatchEvent, data)

    async def close(self):
        if self._cr is not None:
            await self._cr.close()
            self._cr = None


async def unary_rpc(cli: JobHubClient, path: str, req: bytes) -> bytes | CodeError:
    cw, rr = await cli.do_rpc(path)
    try:
        await cw.write_data_part("", req)
        await cw.send_eof()

        resp = await rr.get()
        if isinstance(resp, CodeError):
            return resp

        resp_part = await resp.next_data_part()
        if resp_part is None:
            return CodeError("InvalidResponse", "No response part")

        _, data = resp_part
        return data
    finally:
        await cw.close()
        await rr.close()
