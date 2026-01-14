from dataclasses import dataclass
from typing import List, Any

from jcclang.core.const import SourceType


@dataclass
class VirtualFileParams:
    block_size: int = 4 * 1024 * 1024
    mem_cache_bytes: int = 64 * 1024 * 1024 * 1024
    use_disk_cache: bool = True
    disk_segment_size: int = 1024 * 1024 * 1024
    disk_cache_dir: str | None = None
    validate_func = None
    hot_threshold: int = 16
    decay_interval: int = 60
    async_workers: int = 4
    prefetch_workers: int = 2
    prefetch_count: int = 2


# 单个源对象
@dataclass
class Source:
    path: str = ""
    object_id: int = 0
    type: SourceType = SourceType.JCS
    label: int = ""


# 多个源集合
@dataclass
class Sources:
    items: List[Source]

    @classmethod
    def from_dict_list(cls, data: List[dict[str, Any]]):
        """允许从 dict 列表创建 Sources"""
        items = []
        for d in data:
            # 如果 'type' 是字符串，转换成枚举类型
            if isinstance(d.get("type"), str):
                d["type"] = SourceType[d["type"]]
            items.append(Source(**d))
        return cls(items=items)
