import trio
from jcclang.core.jobhub.abc import (
    IRawConnection,
    IEncrypter,
    IDecrypter,
    IMuxedStream,
)
from jcclang.core.io.abc import ReadCloser, ReadWriteCloser, WriteCloser
from jcclang.core.io.ext import ReadWriterExt
from .yamux.exceptions import RawConnError


class NoiseConn(IRawConnection):
    def __init__(
        self,
        raw_conn: trio.SocketStream,
        rw: ReadWriterExt,
        is_initiator: bool,
        enc: IEncrypter,
        dec: IDecrypter,
    ):
        self._raw_conn = raw_conn
        self._rw = rw
        self.is_initiator = is_initiator
        self._enc = enc
        self._dec = dec
        self.read_buf = None
        self.write_lock = trio.Lock()

    async def read(self, n: int | None = None) -> bytes:
        try:
            if self.read_buf is None:
                len_bytes = await self._rw.read_exactly(2)
                frame_len = int.from_bytes(len_bytes, byteorder="big")

                data = await self._rw.read_exactly(frame_len)
                self.read_buf = self._dec(data)

            if n is None or n >= len(self.read_buf):
                data = self.read_buf
                self.read_buf = None
                return data
            else:
                data = self.read_buf[:n]
                self.read_buf = self.read_buf[n:]
                if len(self.read_buf) == 0:
                    self.read_buf = None
                return data
        except (trio.BrokenResourceError, trio.ClosedResourceError) as e:
            raise RawConnError(e)

    async def write(self, data: bytes) -> None:
        async with self.write_lock:
            data2 = data

            try:
                while data2 is not None:
                    data2 = await self._write_most(data2, 4 * 1024 - 28 - 2)
            except (trio.BrokenResourceError, trio.ClosedResourceError) as e:
                raise RawConnError(e)

    async def _write_most(self, data: bytes, max: int) -> bytes | None:
        rest = None
        if len(data) > max:
            rest = data[max:]
            data = data[:max]

        data = self._enc(data)
        len_bytes = len(data).to_bytes(2, byteorder="big")
        await self._rw.write(len_bytes)
        await self._rw.write(data)
        return rest

    async def close(self) -> None:
        await self._raw_conn.aclose()


class MuxStreamReadWriter(ReadWriteCloser, ReadCloser, WriteCloser):
    def __init__(self, conn: IMuxedStream):
        self._conn = conn

    async def read(self, n: int | None = None) -> bytes:
        return await self._conn.read(n)

    async def write(self, data: bytes) -> None:
        await self._conn.write(data)

    async def close(self) -> None:
        await self._conn.close()
