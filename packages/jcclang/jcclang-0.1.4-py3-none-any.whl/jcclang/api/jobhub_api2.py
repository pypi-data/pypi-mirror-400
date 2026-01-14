from jcclang.core.context import *
from jcclang.core.jobhub import JobHubClient, rpc


class JobHubManager:
    def __init__(self, host=get_jobhub_addr(),
                 port=get_jobhub_port(),
                 job_set_id=get_jobhub_jobset_id(),
                 client_id=get_jobhub_job_id(),
                 secret=get_jobhub_secret(), ):
        self.host = host
        self.port = port
        self.job_set_id = job_set_id
        self.client_id = client_id
        self.secret = secret
        self._cli_cm = None
        self._cli = None

    async def __aenter__(self):
        self._cli_cm = JobHubClient.connect(
            self.host, self.port, self.job_set_id, self.client_id, self.secret
        )
        self._cli = await self._cli_cm.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._cli_cm:
            await self._cli_cm.__aexit__(exc_type, exc_val, exc_tb)
        self._cli = None
        self._cli_cm = None

    async def var_set(self, name: str, value: str, revision: int = 0):
        req = rpc.VarSet(name, value, revision)
        return await req.do(self._cli)

    async def var_get(self, name: str):
        req = rpc.VarGet(name)
        return await req.do(self._cli)

    async def open_stream(self, target: str):
        return await self._cli.open_stream(target)

    async def accept_stream(self):
        return await self._cli.accept_stream()
