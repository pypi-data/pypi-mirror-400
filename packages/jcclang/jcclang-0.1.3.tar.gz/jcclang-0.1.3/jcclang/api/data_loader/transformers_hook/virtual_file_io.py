import os
from threading import Lock

from transformers.utils import cached_file as hf_cached_file

from jcclang.core.logger import jcwLogger
from jcclang.core.model import Sources, VirtualFileParams
from jcclang.virtualfile.virtual_file import VirtualFile


class VirtualFileWrapper:
    """
    对 VirtualFile 做 PathLike 包装：
    - tokenizer 文件必须完整缓存一次
    - 模型权重文件可以按需分块读取
    """
    def __init__(self, vf: VirtualFile, filename: str, full_cache=False):
        self.vf = vf
        self.lock = Lock()
        self.full_cache = full_cache
        self.local_path = os.path.join("./virtual_model", filename.replace("/", "_"))
        os.makedirs(os.path.dirname(self.local_path), exist_ok=True)
        self.size = getattr(vf, "file_size", None)
        if self.full_cache:
            # 一次性写入完整文件
            self._ensure_cache(0, self.size)

    def _ensure_cache(self, start: int = 0, length: int = 4 * 1024 * 1024):
        """
        按需写入指定偏移块
        """
        with self.lock:
            if not os.path.exists(self.local_path):
                with open(self.local_path, "wb") as f:
                    if self.size is not None:
                        f.truncate(self.size)

            self.vf.seek(start)
            data = self.vf.read(length)
            if data:
                with open(self.local_path, "r+b") as f:
                    f.seek(start)
                    f.write(data)

    # PathLike 接口
    def __fspath__(self):
        # 默认写入前 4MB；full_cache 文件已一次写完
        if not self.full_cache:
            self._ensure_cache(0, 4 * 1024 * 1024)
        return self.local_path

    def __str__(self):
        return self.local_path


# def virtual_cached_file(
#         pretrained_model_name_or_path,
#         filename,
#         *,
#         sources=None,
#         vparams=None,
#         **kwargs
# ):
#     """
#     替代 transformers.utils.cached_file
#     根据 sources 信息，动态加载 VirtualFile 而非本地磁盘。
#     """
#
#     jcwLogger.debug(f"virtual_cached_file: {pretrained_model_name_or_path} {filename}")
#
#     if sources is None:
#         sources = Sources.from_dict_list([
#             {"path": "tokenizer_config.json", "object_id": 33194, "type": "JCS"},
#             {"path": "tokenizer.json", "object_id": 33193, "type": "JCS"},
#             {"path": "generation_config.json", "object_id": 33192, "type": "JCS"},
#             {"path": "configuration.json", "object_id": 33191, "type": "JCS"},
#             {"path": "config.json", "object_id": 33190, "type": "JCS"},
#             {"path": "vocab.json", "object_id": 33189, "type": "JCS"},
#             {"path": "model.safetensors", "object_id": 33188, "type": "JCS"}
#         ])
#         vparams = VirtualFileParams()
#
#     # 1. 查找 sources 中匹配的文件
#     matched = None
#     for s in sources.items:
#         if os.path.basename(s.path) == filename:
#             matched = s
#             break
#
#     if matched is None:
#         # 兜底：仍然使用原始逻辑（例如加载 tokenizer_config.json）
#         return hf_cached_file(pretrained_model_name_or_path, filename, **kwargs)
#
#     # 2. 创建 VirtualFile
#     vfile = VirtualFile(matched, vparams)
#
#     wrapper = VirtualFileWrapper(vfile, filename)
#
#     print()
#
#     # ⚠️ 返回路径，而不是对象
#     return os.fspath(wrapper)


def virtual_cached_file(pretrained_model_name_or_path, filename, *, sources=None, vparams=None, **kwargs):
    """
    替代 transformers.cached_file：
    - tokenizer 文件 full_cache=True
    - 模型权重文件 full_cache=False
    """
    jcwLogger.debug(f"virtual_cached_file: {pretrained_model_name_or_path} {filename}")

    if sources is None:
        sources = Sources.from_dict_list([
            {"path": "tokenizer_config.json", "object_id": 33199, "type": "JCS"},
            {"path": "tokenizer.json", "object_id": 33198, "type": "JCS"},
            {"path": "generation_config.json", "object_id": 33197, "type": "JCS"},
            {"path": "configuration.json", "object_id": 33196, "type": "JCS"},
            {"path": "config.json", "object_id": 33195, "type": "JCS"},
            {"path": "vocab.json", "object_id": 33200, "type": "JCS"},
            {"path": "model.safetensors", "object_id": 33188, "type": "JCS"}
        ])
        vparams = VirtualFileParams()

    # 查找对应 Source
    matched = next((s for s in sources.items if os.path.basename(s.path) == filename), None)
    if matched is None:
        # fallback 原始逻辑
        return hf_cached_file(pretrained_model_name_or_path, filename, **kwargs)

    # 创建 VirtualFile
    vfile = VirtualFile(matched, vparams)

    # tokenizer 文件必须完整写入
    if filename.endswith((".json", ".txt")):
        wrapper = VirtualFileWrapper(vfile, filename, full_cache=True)
    else:
        # 模型权重文件可以按需分块
        wrapper = VirtualFileWrapper(vfile, filename, full_cache=False)

    return os.fspath(wrapper)
