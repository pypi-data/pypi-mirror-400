import traceback
from contextlib import AsyncExitStack
from typing import Optional, AsyncIterator, Callable, Awaitable, Any

import trio

from jcclang.core.context import get_jobhub_addr, get_jobhub_port, get_jobhub_secret, get_jobhub_job_id, \
    get_jobhub_jobset_id
from jcclang.core.jobhub import JobHubClient, rpc


class JobHubAPI:
    """
    高层封装的 JobHub 异步 API
    支持：
      - 懒加载连接
      - 自动重连
      - VarSet / VarGet / VarWatch 封装
    """

    def __init__(self, host: str, port: int, group_id: str, client_id: str, secret: bytes):
        self._host = host
        self._port = port
        self._group_id = group_id
        self._client_id = client_id
        self._secret = secret

        self._cli: Optional[JobHubClient] = None
        self._lock = trio.Lock()
        self._reconnect_lock = trio.Lock()
        self._closed = False

        # 用于限制频繁重连
        self._reconnect_attempts = 0
        self._cli_cm = None  # 保存 context manager 对象
        self._exit_stack = AsyncExitStack()  # 管理退出

    # --------------------------
    # 内部工具方法
    # --------------------------

    async def _ensure_client(self) -> JobHubClient | None:
        """懒加载 + 自动重连的核心"""
        if self._closed:
            raise RuntimeError("JobHubAPI 已关闭")

        if self._cli is not None and not self._cli.is_closed():
            return self._cli

        async with self._lock:
            # 再次检查，避免竞争
            if self._cli is None or self._cli.is_closed():
                await self._connect_with_retry()
        return self._cli

    # async def _connect_with_retry(self):
    #     """尝试重连，带指数退避"""
    #     delay = min(2 ** self._reconnect_attempts, 30)
    #     if self._reconnect_attempts > 0:
    #         print(f"[JobHubAPI] 正在重连... 第 {self._reconnect_attempts} 次，等待 {delay}s")
    #         await trio.sleep(delay)
    #     try:
    #         async with JobHubClient.connect(
    #                 host=self._host,
    #                 port=self._port,
    #                 job_set_id=self._group_id,
    #                 local_job_id=self._client_id,
    #                 shared_secret=self._secret,
    #         ) as cli:
    #             self._cli = cli
    #         # self._cli = await JobHubClient.connect(
    #         #     host=self._host, port=self._port,
    #         #     job_set_id=self._group_id, local_job_id=self._client_id,
    #         #     shared_secret=self._secret)
    #         # print("[JobHubAPI] 连接成功")
    #         self._reconnect_attempts = 0
    #     except Exception as e:
    #         print(f"[JobHubAPI] 连接失败: {e}")
    #         traceback.print_exc()
    #         self._reconnect_attempts += 1
    #         raise

    async def _connect_with_retry(self):
        """尝试重连，带指数退避"""
        delay = min(2 ** self._reconnect_attempts, 30)
        if self._reconnect_attempts > 0:
            print(f"[JobHubAPI] 正在重连... 第 {self._reconnect_attempts} 次，等待 {delay}s")
            await trio.sleep(delay)

        try:
            cm = JobHubClient.connect(
                host=self._host,
                port=self._port,
                job_set_id=self._group_id,
                local_job_id=self._client_id,
                shared_secret=self._secret,
            )
            cli = await self._exit_stack.enter_async_context(cm)
            self._cli_cm = cm
            self._cli = cli
            print("[JobHubAPI] 连接成功")
            self._reconnect_attempts = 0
        except Exception as e:
            print(f"[JobHubAPI] 连接失败: {e}")
            traceback.print_exc()
            self._reconnect_attempts += 1
            raise

    async def _safe_call(self, func: Callable[[JobHubClient], Awaitable[Any]], retry_once=True):
        """
        包装 RPC 调用，自动检测连接失效并重连一次
        """
        cli = await self._ensure_client()
        try:
            return await func(cli)
        except Exception as e:
            # 网络断开、EOF 等异常都触发重连
            print(f"[JobHubAPI] 调用异常：{type(e).__name__} - {e}")
            try:
                await self._reconnect()
            except Exception as e2:
                print(f"[JobHubAPI] 重连失败: {e2}")
                raise

            if retry_once:
                print("[JobHubAPI] 正在重试 RPC ...")
                cli = await self._ensure_client()
                return await func(cli)
            raise

    async def _reconnect(self):
        """单独暴露的重连函数，带锁保护"""
        async with self._reconnect_lock:
            if self._cli and not self._cli.is_closed():
                return
            await self._connect_with_retry()

    # async def close(self):
    #     """关闭底层连接"""
    #     self._closed = True
    #     if self._cli is not None:
    #         try:
    #             await self._cli.close()
    #         except Exception:
    #             pass
    #         self._cli = None

    async def close(self):
        """关闭底层连接"""
        self._closed = True
        try:
            await self._exit_stack.aclose()  # Ensure all context managers are closed
        except Exception as e:
            print(f"[JobHubAPI] 关闭时发生错误: {e}")
            traceback.print_exc()
        finally:
            self._cli = None
            self._cli_cm = None

    # --------------------------
    # 封装接口：VarSet / VarGet / VarWatch
    # --------------------------

    async def var_set(self, name: str, value: str, revision: int = 0):
        """设置变量值"""

        async def _run(cli):
            req = rpc.VarSet(name, value, revision)
            return await req.do(cli)

        return await self._safe_call(_run, retry_once=True)

    async def var_get(self, name: str):
        """获取变量值"""

        async def _run(cli):
            req = rpc.VarGet(name)
            return await req.do(cli)

        return await self._safe_call(_run, retry_once=True)

    async def var_watch(self, name: str) -> AsyncIterator[rpc.VarWatchEvent]:
        """
        监听变量变化（异步生成器）
        如果连接中断，将自动重连并重新订阅 watch
        """
        watcher: Optional[rpc.VarWatch] = None

        while not self._closed:
            try:
                cli = await self._ensure_client()
                watcher = rpc.VarWatch(name)
                err = await watcher.do(cli)
                if err:
                    print(f"[JobHubAPI] VarWatch 错误: {err}")
                    await trio.sleep(2)
                    continue

                while True:
                    event = await watcher.next()
                    if event is None:
                        print("[JobHubAPI] watch 通道结束，尝试重连")
                        break
                    yield event

            except Exception as e:
                print(f"[JobHubAPI] watch 异常: {e}")
                traceback.print_exc()
                await self._reconnect()
                await trio.sleep(2)
                continue

            finally:
                if watcher:
                    await watcher.close()
                watcher = None

    # --------------------------
    # 封装接口：open_stream / accept_stream
    # --------------------------

    async def open_stream(self, dst_job_id: str, name: str = "", timeout_sec: int = 15):
        """
        打开到指定 Job 的流（client -> client）
        若连接断开，会自动重连并重试一次。
        """

        async def _run(cli):
            return await cli.open_stream(dst_job_id, name, timeout_sec)

        # 使用通用的安全包装，自动重连一次
        return await self._safe_call(_run, retry_once=True)

    async def accept_stream(self, name: str = ""):
        """
        等待接收来自其他 Job 的流（server 端）
        若连接断开，会自动重连并继续等待。
        """
        while not self._closed:
            try:
                cli = await self._ensure_client()
                stream = await cli.accept_stream(name)
                print(f"[JobHubAPI] 接收到流: {stream.name()}")
                return stream
            except trio.ClosedResourceError:
                print("[JobHubAPI] accept_stream: 客户端关闭，尝试重连")
                await self._reconnect()
                await trio.sleep(1)
                continue
            except Exception as e:
                print(f"[JobHubAPI] accept_stream 异常: {e}")
                traceback.print_exc()
                await self._reconnect()
                await trio.sleep(2)
                continue
        raise trio.ClosedResourceError("JobHubAPI 已关闭")


# --------------------------
# 全局单例访问器
# --------------------------

_jobhub_instance: Optional[JobHubAPI] = None
_api_lock = trio.Lock()


async def jobhub_instance() -> JobHubAPI:
    """获取全局 API 单例（懒加载 + 自动重连）"""
    global _jobhub_instance
    if _jobhub_instance is not None:
        return _jobhub_instance

    async with _api_lock:
        if _jobhub_instance is None:
            _jobhub_instance = JobHubAPI(
                host=get_jobhub_addr(),
                port=get_jobhub_port(),
                group_id=get_jobhub_jobset_id(),
                client_id=get_jobhub_job_id(),
                secret=get_jobhub_secret(),
            )
    return _jobhub_instance


async def close_jobhub_instance():
    """关闭全局 API"""
    global _jobhub_instance
    if _jobhub_instance:
        await _jobhub_instance.close()
        _jobhub_instance = None
