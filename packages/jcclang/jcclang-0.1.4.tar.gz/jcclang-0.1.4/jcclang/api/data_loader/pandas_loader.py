import io

import pandas as pd

from jcclang.core.model import VirtualFileParams, Source
from jcclang.virtualfile.virtual_file import VirtualFile


class Pandas:
    """虚拟化的 pandas I/O 层"""

    def __init__(self, source: Source, virtual_file_params: VirtualFileParams = None):
        if virtual_file_params is None:
            virtual_file_params = VirtualFileParams()
        self.virtual_file_params = virtual_file_params
        self.source = source

    def _open_virtual(self):
        """返回一个基于 VirtualFile 的文件对象"""
        vf = VirtualFile(source=self.source, params=self.virtual_file_params)
        return vf

    def _read_bytes(self) -> bytes:
        """统一从虚拟文件系统读取数据"""
        vf = self._open_virtual()
        data = vf.read()
        vf.close()
        return data

    # ==============================
    # Pandas-like API
    # ==============================

    def read_csv(self, **kwargs) -> pd.DataFrame:
        raw = self._read_bytes()
        buf = io.BytesIO(raw)
        return pd.read_csv(buf, **kwargs)

    def read_json(self, **kwargs) -> pd.DataFrame:
        raw = self._read_bytes()
        buf = io.BytesIO(raw)
        return pd.read_json(buf, **kwargs)

    def read_parquet(self, **kwargs) -> pd.DataFrame:
        raw = self._read_bytes()
        buf = io.BytesIO(raw)
        return pd.read_parquet(buf, **kwargs)

    def read_excel(self, **kwargs) -> pd.DataFrame:
        raw = self._read_bytes()
        buf = io.BytesIO(raw)
        return pd.read_excel(buf, **kwargs)
