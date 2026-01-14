from jcclang.core.jobhub.jobhub import JobHubClient
import jcclang.core.jobhub.rpc as rpc
from jcclang.core.jobhub.types import JobStream


class Var:
    def __init__(self, name: str, cli: JobHubClient):
        self._name = name
        self._cli = cli
        self._value = ""
        self._revision = 0

    # 变量名。
    def name(self):
        return self._name

    # 变量的值。
    def value(self):
        return self._value

    # 变量的版本号，如果为0，代表变量在远端不存在值。
    def revision(self):
        return self._revision

    # 设置变量值，返回设置之后的结果
    async def set(self, value: str) -> str:
        req = rpc.VarSet(name=self._name, value=value)
        resp = await req.do(self._cli)
        if isinstance(resp, rpc.VarSetResp):
            self._value = value
            self._revision = resp.revision
            return value
        else:
            raise resp

    # 仅当远端变量的版本号与当前一致时，才设置新变量值。
    # 如果load_latest为True，则在发现不一致时，强制加载最新版本的变量值。
    async def rev_set(self, value: str, load_latest: bool = False) -> bool:
        req = rpc.VarSet(name=self._name, value=value, revision=self._revision)
        resp = await req.do(self._cli)
        if isinstance(resp, rpc.VarSetResp):
            if resp.ok or load_latest:
                self._value = value
                self._revision = resp.revision
                return True
            return False
        else:
            raise resp

    # 加载最新版本的变量值。
    async def reload(self) -> str:
        req = rpc.VarGet(name=self._name)
        resp = await req.do(self._cli)
        if isinstance(resp, rpc.VarGetResp):
            self._value = resp.value
            self._revision = resp.revision
            return self._value
        else:
            raise resp


class JobHub:
    def __init__(self, cli: JobHubClient):
        self._cli = cli

    # 获取JobHub客户端。
    def client(self):
        return self._cli

    # 获取变量，会加载最新版本的变量值。
    async def get_var(self, name: str) -> Var:
        v = Var(name, self._cli)
        await v.reload()
        return v

    # 打开一个新的流。
    async def open_stream(
        self, target_job_id: str, name: str | None = None
    ) -> JobStream:
        if name is None:
            name = ""
        return await self._cli.open_stream(target_job_id, name)

    # 接受一个新的流
    async def accept_stream(self, name: str | None = None) -> JobStream:
        if name is None:
            name = ""
        return await self._cli.accept_stream(name)
