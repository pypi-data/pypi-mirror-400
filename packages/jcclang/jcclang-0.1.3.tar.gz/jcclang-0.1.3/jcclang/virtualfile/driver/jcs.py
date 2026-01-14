import time

import requests

from jcclang.core.const import JCSAPI
from jcclang.core.context import *
from jcclang.core.logger import jcwLogger
from jcclang.core.utils.presign import SignKey, Presigner
from jcclang.virtualfile.driver.base_driver import Driver


class JCS(Driver):
    def __init__(self, object_id: int):
        """
        HTTP Driver 实现，用于通过HTTP按需读取对象数据。
        """
        self.base_url = get_gateway_addr().rstrip("/")
        self.session = requests.Session()
        self.object_id = object_id
        self._open_files = {}  # file_id -> metadata
        self.read_count = 0
        self.spend_time = 0

    def open(self, path: str, mode: str = "rb") -> str:
        """
        打开一个远程文件。
        path 通常为 objectID，例如 123
        """
        pass

    def stat(self, file_id: str) -> dict:
        """
        获取对象元信息
        """
        meta_url = f"{self.base_url}/storage/object/get"
        params = {
            "objectID": self.object_id,
            "userID": int(get_user_id()),
        }
        resp = self.session.get(meta_url, params=params)
        if resp.status_code != 200:
            jcwLogger.error(f"HTTP request failed: {resp.text}")
            raise IOError(f"Failed to stat object: {resp.text}")
        meta = resp.json().get("data").get("object")

        jcwLogger.debug(f"Stat object: {self.object_id}, size: {meta.get('size', 0)}")

        return {
            "size": int(meta.get("size", 0)),
            "packageID": meta.get("packageID", 0),
            "fileHash": meta.get("fileHash", None),
        }

    def read(self, file_id: str = None, offset: int = None, length: int = None) -> bytes:
        """
        从远程对象读取指定范围数据。
        """
        jcwLogger.debug(f"Read object: {self.object_id}, offset: {offset}, length: {length}")
        self.read_count += 1

        sk = SignKey(get_jcs_ak(), get_jcs_sk())
        presigner = Presigner(get_jcs_addr(), sk)

        params = {
            "objectID": self.object_id,
            "offset": offset,
            "length": length,
        }
        presign_url = presigner.presign(params, JCSAPI.PRESIGNED, "GET", 3600)

        resp = None
        for i in range(3):
            resp = self.session.get(presign_url, stream=True, verify=False)
            if resp.status_code == 200:
                break
            jcwLogger.error(f"HTTP read failed: {resp.text}")
            time.sleep(3)
        if resp.status_code != 200:
            raise IOError(f"HTTP read failed: {resp.text}")
        return resp.content

    def close(self, file_id: str) -> None:
        """
        关闭对象，释放缓存。
        """
        jcwLogger.debug(f"Close object: {self.object_id}")
        jcwLogger.debug(f"Read count: {self.read_count}")
        jcwLogger.debug(f"Sign spend time: {self.spend_time}")
        pass
