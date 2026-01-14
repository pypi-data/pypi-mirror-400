import io

from jcclang.core.model import Sources, VirtualFileParams
from jcclang.virtualfile.virtual_file import VirtualFile


class VirtualFileIO(io.RawIOBase):
    """
    用 VirtualFile 封装成类文件对象，支持 seek/tell/read。
    """

    def __init__(self, vf: VirtualFile):
        self.vf = vf
        self.closed_flag = False

    def read(self, size=-1):
        return self.vf.read(size)

    def seek(self, offset, whence=0):
        self.vf.seek(offset, whence)
        return self.vf.tell()

    def tell(self):
        return self.vf.tell()

    def close(self):
        if not self.closed_flag:
            self.vf.close()
            self.closed_flag = True

    @property
    def closed(self):
        return self.closed_flag


def virtual_cached_file(pretrained_model_name_or_path, filename, **kwargs):
    """
    替代 transformers.utils.cached_file。
    从 VirtualFile 系统获取指定文件内容，返回 BytesIO 对象。
    """
    sources: Sources = kwargs.pop("sources")
    vparams: VirtualFileParams = kwargs.pop("vparams")

    # 找到对应 Source
    src_map = {s.path: s for s in sources.items}
    if filename not in src_map:
        # 尝试只匹配文件名（去掉路径）
        file_name_only_map = {s.path.split("/")[-1]: s for s in sources.items}
        src = file_name_only_map.get(filename)
        if src is None:
            raise FileNotFoundError(f"{filename} not found in virtual sources")
    else:
        src = src_map[filename]

    vf = VirtualFile(src, params=vparams)
    # 直接返回类文件对象，支持 seek/read
    return VirtualFileIO(vf)
