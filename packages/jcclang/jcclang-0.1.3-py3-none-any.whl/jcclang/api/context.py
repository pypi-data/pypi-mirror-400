import trio
from api.jobhub import JobHub


class Context:
    def __init__(
        self, nursery: trio.Nursery, job_set_id: str, job_id: str, job_hub: JobHub
    ):
        self._nursery = nursery
        self._job_set_id = job_set_id
        self._job_id = job_id
        self._job_hub = job_hub

    def nursery(self):
        return self._nursery

    def job_set_id(self) -> str:
        return self._job_set_id

    def job_id(self) -> str:
        return self._job_id

    def job_hub(self) -> JobHub:
        return self._job_hub
