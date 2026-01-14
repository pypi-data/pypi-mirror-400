from .utils import StreamReadWriter
from .abc import (
    Closer,
    ReadCloser,
    ReadWriteCloser,
    ReadWriter,
    Reader,
    WriteCloser,
    Writer,
)
from trio.abc import Stream
from typing_extensions import (
    Self,
)


class ReaderExt(Reader):
    def __init__(self, reader: Reader):
        self.reader = reader

    async def read(self, n: int = 1024) -> bytes:
        return await self.reader.read(n)

    async def read_exactly(self, n: int) -> bytes:
        data = bytearray()
        while len(data) < n:
            chunk = await self.read(n - len(data))
            if not chunk:
                raise EOFError("End of stream reached")
            data += chunk
        return bytes(data)

    async def read_u16_be(self) -> int:
        data = await self.read_exactly(2)
        return int.from_bytes(data, byteorder="big")

    async def read_u16_le(self) -> int:
        data = await self.read_exactly(2)
        return int.from_bytes(data, byteorder="little")

    async def read_u8(self) -> int:
        data = await self.read_exactly(1)
        return data[0]

    async def read_string_u8(self) -> str:
        length = await self.read_u8()
        data = await self.read_exactly(length)
        return data.decode()


class WriterExt(Writer):
    def __init__(self, writer: Writer):
        self.writer = writer

    async def write(self, data: bytes) -> None:
        await self.writer.write(data)

    async def write_u32_be(self, value: int):
        data = value.to_bytes(4, byteorder="big")
        await self.write(data)

    async def write_u16_be(self, value: int):
        data = value.to_bytes(2, byteorder="big")
        await self.write(data)

    async def write_u16_le(self, value: int):
        data = value.to_bytes(2, byteorder="little")
        await self.write(data)

    async def write_u8(self, value: int):
        data = bytes([value])
        await self.write(data)

    async def write_string_u8(self, value: str):
        data = value.encode()
        await self.write_u8(len(data))
        await self.write(data)


class ReadWriterExt(ReaderExt, WriterExt):
    def __init__(self, rw: ReadWriter):
        ReaderExt.__init__(self, rw)
        WriterExt.__init__(self, rw)

    @classmethod
    def from_stream(cls, str: Stream) -> Self:
        return cls(StreamReadWriter(str))


class ReadWriteCloserExt(ReadWriterExt, ReadCloser, WriteCloser, Closer):
    def __init__(self, rw: ReadWriteCloser):
        ReadWriterExt.__init__(self, rw)
        self._closer = rw

    async def close(self) -> None:
        await self._closer.close()
