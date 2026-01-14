import hashlib
import json
import os
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor

from jcclang.core.const import SourceType
from jcclang.core.logger import jcwLogger
from jcclang.core.model import VirtualFileParams, Source
from jcclang.virtualfile.block_fetcher import BlockFetcher
from jcclang.virtualfile.cache_mgr import HybridCacheMgr
from jcclang.virtualfile.driver.jcs import JCS


def _choose_driver(driver: Source):
    if driver.type == SourceType.LOCAL:
        return None
    elif driver.type == SourceType.JCS:
        return JCS(driver.object_id)
    else:
        raise ValueError(f"不支持的URL: {driver}")


def _get_dict_hash(d):
    if d is None:
        return ""
    json_str = json.dumps(d, sort_keys=True)
    hash_value = hashlib.md5(json_str.encode('utf-8')).hexdigest()
    return hash_value


def _make_key(block_id: int, info_hash: str) -> str:
    # key格式可以自定义；现在使用block_id的字符串形式
    return f"{info_hash}_{block_id}"


class VirtualFile:
    def __init__(
            self,
            source: Source,
            params: VirtualFileParams
    ):
        self.source = source
        self.lock = threading.RLock()
        self.closed = False
        if source.type == SourceType.LOCAL:
            self.open_file = open(source.path, "rb")
            return
        # 选择驱动
        driver = _choose_driver(source)
        self.driver = driver
        self.block_size = params.block_size

        # 打开文件
        self.file_id = driver.open(source.path, "rb")
        self.file_info = driver.stat(self.file_id)
        self.file_info_hash = _get_dict_hash(self.file_info)
        self.file_size = self.file_info.get("size", 0)

        # 磁盘缓存目录默认值
        if params.disk_cache_dir is None:
            params.disk_cache_dir = os.path.join(tempfile.gettempdir(), "jcweaver_diskcache")

        self.cache = HybridCacheMgr(
            mem_max_bytes=params.mem_cache_bytes,
            block_size=params.block_size,
            use_disk_cache=params.use_disk_cache,
            disk_root=params.disk_cache_dir,
            file_hash=self.file_info_hash,
            disk_segment_size=params.disk_segment_size,
            validate_func=params.validate_func,
            hot_threshold=params.hot_threshold,
            decay_interval=params.decay_interval,
            async_workers=params.async_workers
        )

        # BlockFetcher 负责从Driver读取块
        self.fetcher = BlockFetcher(self.driver, params.block_size, max_workers=params.prefetch_workers)

        # 预取和锁
        self.prefetch_count = params.prefetch_count
        self.prefetch_executor = ThreadPoolExecutor(max_workers=params.prefetch_workers)

        # 状态
        self.position = 0

    # ========== 文件类API ==========
    def read(self, size: int = -1) -> bytes:
        """
        从当前位置读取 size 字节：
        - 先查内存（cache.get）
        - 再查磁盘（由 cache.get 内部完成）
        - 未命中则 fetcher.fetch_block，然后 cache.put(..., write_to_disk=True)
        """
        jcwLogger.debug("VirtualFile.read(size={})".format(size))

        # 如果source.Type == LOCAL，则打开文件，直接返回文件内容
        if self.source.type == SourceType.LOCAL:
            return self.open_file.read()

        if self.closed:
            raise ValueError("文件已关闭")

        with self.lock:
            if size is None or size < 0:
                size = self.file_size - self.position
            if self.position >= self.file_size:
                return b""

            start_offset = self.position
            end_offset = min(self.file_size, start_offset + size)
            out_parts = []
            cur = start_offset

            while cur < end_offset:
                block_id = cur // self.block_size
                inner = cur % self.block_size
                to_take = min(end_offset - cur, self.block_size - inner)

                # 1) 尝试从缓存获取 (HybridCacheMgr.get 支持验证标志)
                block = self.cache.get(_make_key(block_id, self.file_info_hash), block_id, validate=False)
                if block is None:
                    # 2) 检查是否有正在进行的预取请求：
                    #    (我们在这里不维护预取的future; BlockFetcher可以扩展来暴露它们)
                    # 3) 从驱动获取
                    block = self.fetcher.fetch_block(self.file_id, block_id)
                    # 放入缓存；让缓存决定是否写入磁盘
                    # write_to_disk=True 以便后续进程/周期可以命中磁盘
                    try:
                        # 增强API: put(block_id, data, version=None, write_to_disk=True)
                        self.cache.put(_make_key(block_id, self.file_info_hash), block_id, block, version=None,
                                       write_to_disk=True)
                    except TypeError:
                        # 向后兼容: 旧版本的 HybridCacheMgr 可能使用 put(block_id, data) 签名
                        self.cache.put(_make_key(block_id, self.file_info_hash), block_id, block)

                # 切片并添加
                piece = block[inner: inner + to_take]
                out_parts.append(piece)
                cur += len(piece)

                # 异步预取后续块（仅在顺序读取时）
                next_block = block_id + 1
                max_block_index = (self.file_size - 1) // self.block_size if self.file_size else None
                if (max_block_index is None) or (next_block <= max_block_index):
                    # 预取一个块窗口；对于预取我们避免立即写入磁盘
                    for i in range(1, self.prefetch_count + 1):
                        pbi = block_id + i
                        if max_block_index is not None and pbi > max_block_index:
                            break
                        # 提交预取：在预取内部实际获取前检查是否存在
                        self.prefetch_executor.submit(self._prefetch_block, pbi)

            # 前进位置
            read_len = sum(len(p) for p in out_parts)
            self.position += read_len
            return b"".join(out_parts)

    def _prefetch_block(self, block_id: int):
        jcwLogger.debug("VirtualFile._prefetch_block(block_id={})".format(block_id))
        # 如果已在内存或磁盘缓存中，跳过
        if self.cache.get(_make_key(block_id, self.file_info_hash), block_id) is not None:
            return
        try:
            data = self.fetcher.fetch_block(self.file_id, block_id)
            try:
                self.cache.put(_make_key(block_id, self.file_info_hash), block_id, data, version=None,
                               write_to_disk=True)
            except TypeError:
                # 简单缓存实现的回退
                self.cache.put(_make_key(block_id, self.file_info_hash), block_id, data)
        except Exception as e:
            # 吞掉预取异常
            jcwLogger.error("VirtualFile._prefetch_block(block_id={}) 预取异常: {}".format(block_id, e))
            pass

    def seek(self, offset: int, whence: int = 0):
        jcwLogger.debug("VirtualFile.seek(offset={}, whence={})".format(offset, whence))
        with self.lock:
            if whence == 0:
                pos = offset
            elif whence == 1:
                pos = self.position + offset
            elif whence == 2:
                pos = (self.file_size or 0) + offset
            else:
                raise ValueError("无效的whence")
            if pos < 0:
                raise ValueError("负位置")
            self.position = min(pos, self.file_size)

    def tell(self) -> int:
        jcwLogger.debug("VirtualFile.tell()")
        with self.lock:
            return self.position

    def close(self):
        jcwLogger.debug("VirtualFile.close()")

        if self.source.type == SourceType.LOCAL:
            self.open_file.close()
            return

        with self.lock:
            if self.closed:
                return
            # 优先使用sync()，否则使用close()
            if hasattr(self.cache, "sync"):
                try:
                    self.cache.sync()
                except Exception:
                    pass
            elif hasattr(self.cache, "close"):
                try:
                    self.cache.close()
                except Exception:
                    pass
            try:
                self.fetcher.shutdown()
            except Exception:
                pass
            try:
                self.prefetch_executor.shutdown(wait=False)
            except Exception:
                pass
            try:
                self.driver.close(self.file_id)
            except Exception:
                pass
            self.closed = True
