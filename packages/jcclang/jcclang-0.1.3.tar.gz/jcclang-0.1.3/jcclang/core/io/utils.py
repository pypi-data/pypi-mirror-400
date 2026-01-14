from trio.abc import Stream

from .abc import ReadCloser, ReadWriter, Reader, WriteCloser, Writer


class StreamReadWriter(ReadWriter):
    def __init__(self, stream: Stream):
        self._stream = stream

    async def read(self, n: int) -> bytes:
        return await self._stream.receive_some(n)

    async def write(self, data: bytes) -> None:
        await self._stream.send_all(data)


class NoopReadCloser(ReadCloser):
    def __init__(self, reader: Reader):
        self._reader = reader

    async def read(self, n: int | None = None) -> bytes:
        return await self._reader.read(n)

    async def close(self):
        pass


class NoopWriteCloser(WriteCloser):
    def __init__(self, writer: Writer):
        self._writer = writer

    async def write(self, data: bytes) -> None:
        await self._writer.write(data)

    async def close(self):
        pass
