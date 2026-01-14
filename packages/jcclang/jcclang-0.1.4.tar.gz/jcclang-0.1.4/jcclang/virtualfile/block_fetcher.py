import concurrent.futures

from jcclang.core.logger import jcwLogger
from jcclang.virtualfile.driver.base_driver import Driver


class BlockFetcher:
    def __init__(self, driver: Driver, block_size: int = 4 * 1024 * 1024, max_workers: int = 4):
        """
        :param driver: 实现了 open/read/close 的底层驱动
        :param block_size: 每个 block 的字节大小
        :param max_workers: 异步读取时的线程池大小
        """
        self.driver = driver
        self.block_size = block_size
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)

    # ------------------------
    # 基础能力
    # ------------------------
    def fetch_block(self, file_id: str, block_index: int) -> bytes:
        """
        获取指定 block 的数据。
        - block_index: 第几个 block（从 0 开始）
        """
        jcwLogger.debug(f"fetch_block: file_id={file_id}, block_index={block_index}")
        offset = block_index * self.block_size
        length = self.block_size
        data = self.driver.read(file_id, offset, length)
        return data

    def fetch_range(self, file_id: str, offset: int, length: int) -> bytes:
        """
        获取任意区间数据（可能跨多个 block）。
        """
        start_block = offset // self.block_size
        end_block = (offset + length - 1) // self.block_size

        result = bytearray()
        for block_idx in range(start_block, end_block + 1):
            block_data = self.fetch_block(file_id, block_idx)
            result.extend(block_data)

        # 截取出真正请求的区间
        start_offset_in_block = offset % self.block_size
        return bytes(result[start_offset_in_block:start_offset_in_block + length])

    # ------------------------
    # 高级特性
    # ------------------------
    def prefetch_blocks(self, file_id: str, start_block: int, count: int) -> list[bytes]:
        """
        批量预取多个连续 block，用于顺序扫描场景。
        """
        blocks = []
        for i in range(count):
            data = self.fetch_block(file_id, start_block + i)
            blocks.append(data)
        return blocks

    def async_fetch(self, file_id: str, block_indices: list[int]):
        """
        异步/并行获取多个 block，内部可用线程池调度。
        返回 dict: {block_index: data}
        """
        futures = {
            idx: self.executor.submit(self.fetch_block, file_id, idx)
            for idx in block_indices
        }
        results = {}
        for idx, fut in futures.items():
            results[idx] = fut.result()
        return results

    def shutdown(self):
        """关闭线程池"""
        jcwLogger.debug("Shutting down BlockFetcher")
        self.executor.shutdown(wait=True)
