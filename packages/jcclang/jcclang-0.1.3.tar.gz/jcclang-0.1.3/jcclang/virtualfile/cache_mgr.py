import io
import json
import os
import threading
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from typing import Callable
from typing import Optional, Dict

from jcclang.core.logger import jcwLogger


class SegmentedDiskCache:
    """
    高性能分段磁盘缓存（动态扩容 + 延迟分配 + 元信息持久化）

    特性：
    - 延迟分配：仅在首次写入时创建段文件
    - 动态扩容：根据最大offset自动增加segment数量
    - 元信息持久化：在meta文件中保存cache状态
    - 支持跨段读写
    """

    META_SUFFIX = ".meta"

    def __init__(
            self,
            root_dir: str,
            base_name: str = "cache",
            segment_size: int = 128 * 1024 * 1024,
            compress: bool = False,
            auto_load_meta: bool = True,
    ):
        self.root_dir = os.path.abspath(root_dir)
        os.makedirs(self.root_dir, exist_ok=True)

        self.base_name = base_name
        self.segment_size = segment_size
        self.compress = compress

        self.lock = threading.RLock()
        self.segment_files: Dict[int, io.BufferedRandom] = {}

        # 元信息路径
        self.meta_path = os.path.join(self.root_dir, f"{self.base_name}{self.META_SUFFIX}")

        # 状态信息
        self.total_size: int = 0
        self.num_segments: int = 0

        # 尝试加载元信息
        if auto_load_meta and os.path.exists(self.meta_path):
            self._load_meta()
        else:
            self._save_meta()

    # ----------------------------------------------------------------------
    # Meta 管理
    # ----------------------------------------------------------------------

    def _save_meta(self):
        """保存缓存元信息"""
        meta = {
            "segment_size": self.segment_size,
            "total_size": self.total_size,
            "num_segments": self.num_segments,
        }
        tmp_path = self.meta_path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)
        os.replace(tmp_path, self.meta_path)

    def _load_meta(self):
        """加载缓存元信息"""
        with open(self.meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        self.segment_size = meta.get("segment_size", self.segment_size)
        self.total_size = meta.get("total_size", 0)
        self.num_segments = meta.get("num_segments", 0)

    # ----------------------------------------------------------------------
    # 段文件管理
    # ----------------------------------------------------------------------

    def _segment_path(self, seg_id: int) -> str:
        return os.path.join(self.root_dir, f"{self.base_name}_{seg_id}.blk")

    def _open_segment(self, seg_id: int):
        """懒加载打开段文件（首次写入时创建）"""
        if seg_id in self.segment_files:
            return self.segment_files[seg_id]

        path = self._segment_path(seg_id)
        os.makedirs(self.root_dir, exist_ok=True)
        if not os.path.exists(path):
            open(path, "wb").close()
        f = open(path, "r+b", buffering=0)
        self.segment_files[seg_id] = f
        return f

    def close(self):
        with self.lock:
            for f in self.segment_files.values():
                try:
                    f.close()
                except Exception:
                    pass
            self.segment_files.clear()
            self._save_meta()

    # ----------------------------------------------------------------------
    # 地址映射
    # ----------------------------------------------------------------------

    def _map_offset(self, offset: int):
        seg_id = offset // self.segment_size
        seg_off = offset % self.segment_size
        return seg_id, seg_off

    # ----------------------------------------------------------------------
    # 核心读写逻辑
    # ----------------------------------------------------------------------

    def read(self, offset: int, size: int) -> bytes:
        jcwLogger.debug(f"Read {size} bytes from {offset}")
        """支持跨段读取"""
        with self.lock:
            buf = bytearray()
            remain = size
            cur_off = offset

            while remain > 0:
                seg_id, seg_off = self._map_offset(cur_off)
                if seg_id >= self.num_segments:
                    break

                f = self._open_segment(seg_id)
                f.seek(seg_off)
                seg_remain = min(remain, self.segment_size - seg_off)
                chunk = f.read(seg_remain)
                buf.extend(chunk)
                cur_off += seg_remain
                remain -= seg_remain

            return bytes(buf)

    def write(self, offset: int, data: bytes):
        jcwLogger.debug(f"Write {len(data)} bytes to {offset}")
        """支持跨段写入 + 自动扩容"""
        with self.lock:
            cur_off = offset
            remain = len(data)
            pos = 0

            while remain > 0:
                seg_id, seg_off = self._map_offset(cur_off)
                f = self._open_segment(seg_id)
                seg_remain = min(remain, self.segment_size - seg_off)

                f.seek(seg_off)
                f.write(data[pos:pos + seg_remain])
                f.flush()

                cur_off += seg_remain
                pos += seg_remain
                remain -= seg_remain

                # 自动扩容段数
                if seg_id + 1 > self.num_segments:
                    self.num_segments = seg_id + 1

            # 更新 total_size
            end_pos = offset + len(data)
            if end_pos > self.total_size:
                self.total_size = end_pos
            self._save_meta()

    def get_or_put(self, offset: int, size: int, fetch_fn) -> bytes:
        """
        从 offset 读取 size 字节；
        如果读取结果为空或为全零，则调用 fetch_fn() 获取数据并写入缓存。
        """
        data = self.read(offset, size)
        if not data or all(b == 0 for b in data):
            new_data = fetch_fn()
            self.write(offset, new_data)
            return new_data
        return data

    # ----------------------------------------------------------------------
    # 统计信息
    # ----------------------------------------------------------------------

    def stats(self):
        with self.lock:
            total_disk = 0
            for seg_id in range(self.num_segments):
                path = self._segment_path(seg_id)
                if os.path.exists(path):
                    total_disk += os.path.getsize(path)
            return {
                "segments": self.num_segments,
                "segment_size": self.segment_size,
                "total_size": self.total_size,
                "disk_usage": total_disk,
                "meta_path": self.meta_path,
            }


class HybridCacheMgr:
    """
    双层缓存（内存 + 磁盘，基于 SegmentedDiskCache）
    支持：
      - LRU 内存缓存（OrderedDict）
      - 异步落盘
      - 热点检测
      - 校验函数 validate_func(key)->version
    """

    def __init__(
            self,
            mem_max_bytes: int,
            block_size: int,
            use_disk_cache: bool,
            disk_root: str,
            file_hash: str,
            disk_segment_size: int,
            validate_func: Optional[Callable[[str], Optional[str]]] = None,
            hot_threshold: int = 16,
            decay_interval: int = 60,
            async_workers: int = 4
    ):
        self.mem_max_bytes = mem_max_bytes
        self.block_size = block_size
        self.mem_cache = OrderedDict()  # key -> bytes
        self.mem_current = 0
        self.lock = threading.RLock()

        self.use_disk_cache = use_disk_cache
        if use_disk_cache:
            self.disk = SegmentedDiskCache(
                root_dir=disk_root,
                base_name=file_hash,
                segment_size=disk_segment_size,
            )
        self.executor = ThreadPoolExecutor(max_workers=async_workers)

        # 版本 & 热点检测
        self.versions = {}
        self.access_counts = {}
        self.pinned = set()
        self.hot_threshold = hot_threshold
        self.decay_interval = decay_interval
        self._stop = threading.Event()
        self._decay_thread = threading.Thread(target=self._decay_loop, daemon=True)
        self._decay_thread.start()

        # stats
        self.mem_hits = 0
        self.disk_hits = 0
        self.misses = 0

        self.validate_func = validate_func
        self.read_count = 0

    # -------------------------
    # 内部辅助函数
    # -------------------------
    def _key_to_offset(self, block_id: int) -> int:
        """
        将 block_id 转换为逻辑偏移位置
        """
        # 可根据需求换成更稳定映射
        return block_id * self.block_size

    def _promote_to_mem(self, key: str, data: bytes, version: Optional[str] = None):
        with self.lock:
            if key in self.mem_cache:
                old = self.mem_cache.pop(key)
                self.mem_current -= len(old)
            self.mem_cache[key] = data
            self.mem_cache.move_to_end(key)
            self.mem_current += len(data)
            if version:
                self.versions[key] = version
            self._evict_if_needed()

    def _evict_if_needed(self):
        while self.mem_current > self.mem_max_bytes and self.mem_cache:
            oldest_key = None
            for k in self.mem_cache.keys():
                if k not in self.pinned:
                    oldest_key = k
                    break
            if oldest_key is None:
                # 强制淘汰最旧
                k, v = self.mem_cache.popitem(last=False)
                self.mem_current -= len(v)
                self.versions.pop(k, None)
                continue
            v = self.mem_cache.pop(oldest_key)
            self.mem_current -= len(v)

    # -------------------------
    # 公共 API
    # -------------------------
    def get(self, key: str, block_id: int, validate: bool = False) -> Optional[bytes]:
        self.read_count += 1
        # 1) 内存缓存
        with self.lock:
            v = self.mem_cache.get(key)
            if v is not None:
                self.mem_cache.move_to_end(key)
                self.mem_hits += 1
                self._record_access(key)
                if validate and self.validate_func:
                    cur = self.validate_func(key)
                    stored = self.versions.get(key)
                    if cur is not None and stored is not None and cur != stored:
                        self._invalidate_locked(key, block_id)
                        self.misses += 1
                        return None
                return v

        # 2) 磁盘缓存
        if self.use_disk_cache:
            offset = self._key_to_offset(block_id)
            data = self.disk.read(offset, self.block_size)
            if data and not all(b == 0 for b in data):
                self.disk_hits += 1
                self._promote_to_mem(key, data)
                self._record_access(key)
                if validate and self.validate_func:
                    cur = self.validate_func(key)
                    stored = self.versions.get(key)
                    if cur is not None and stored is not None and cur != stored:
                        self.invalidate(key, block_id)
                        self.misses += 1
                        return None
                return data

        # 未命中
        self.misses += 1
        return None

    def put(self, key: str, block_id: int, data: bytes, version: Optional[str] = None, write_to_disk: bool = True):
        self._promote_to_mem(key, data, version)
        if self.use_disk_cache and write_to_disk:
            offset = self._key_to_offset(block_id)
            try:
                self.executor_submit(self.disk.write, offset, data)
            except Exception:
                try:
                    self.disk.write(offset, data)
                except Exception:
                    pass

    def invalidate(self, key: str, block_id: int):
        with self.lock:
            self._invalidate_locked(key, block_id)

    def _invalidate_locked(self, key: str, block_id: int):
        if key in self.mem_cache:
            val = self.mem_cache.pop(key)
            self.mem_current -= len(val)
        self.versions.pop(key, None)
        offset = self._key_to_offset(block_id)
        zero_bytes = bytes(self.block_size)
        try:
            self.disk.write(offset, zero_bytes)
        except Exception:
            pass

    # -------------------------
    # 热点检测
    # -------------------------
    def _record_access(self, key: str):
        with self.lock:
            cnt = self.access_counts.get(key, 0) + 1
            self.access_counts[key] = cnt
            if cnt >= self.hot_threshold:
                self.pinned.add(key)

    def _decay_loop(self):
        while not self._stop.wait(self.decay_interval):
            with self.lock:
                for k in list(self.access_counts.keys()):
                    v = self.access_counts[k] >> 1
                    if v <= 0:
                        self.access_counts.pop(k, None)
                        self.pinned.discard(k)
                    else:
                        self.access_counts[k] = v

    # -------------------------
    # 辅助函数和关闭
    # -------------------------
    def executor_submit(self, fn, *args, **kwargs):
        if not hasattr(self, "_executor") or self._executor is None:
            self._executor = ThreadPoolExecutor(max_workers=4)
        return self._executor.submit(fn, *args, **kwargs)

    def stats(self):
        with self.lock:
            return {
                "mem": {"items": len(self.mem_cache), "bytes": self.mem_current},
                "disk": self.disk.stats(),
                "mem_hits": self.mem_hits,
                "disk_hits": self.disk_hits,
                "misses": self.misses,
                "pinned": len(self.pinned),
                "access_counts": len(self.access_counts)
            }

    def close(self):
        jcwLogger.debug(f"read cache count: {self.read_count}")
        self._stop.set()
        try:
            self._decay_thread.join(timeout=1.0)
        except Exception:
            pass
        if hasattr(self, "_executor") and self._executor:
            try:
                self._executor.shutdown(wait=True)
            except Exception:
                pass
        self.disk.close()
