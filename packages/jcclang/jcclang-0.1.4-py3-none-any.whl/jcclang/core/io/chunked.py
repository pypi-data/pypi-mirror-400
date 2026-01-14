from enum import Enum
from typing import Callable

from .ext import ReadWriterExt, ReaderExt, WriterExt
from .abc import ReadCloser, Reader, WriteCloser


class PartType(Enum):
    Error = 0xFF
    EOF = 0x00
    NewPart = 0x01
    Data = 0x02
    PartEOF = 0x03


class PartReader:
    def __init__(
        self,
        re: ReaderExt,
        next_part_callbak: Callable[[bytes | Exception | None, bool], None],
    ):
        self._re = re
        self._next_part_callbak = next_part_callbak
        self._part_len = 0
        self._part_read_len = 0
        self._eof = False
        self._err = None

    async def read(self, n: int | None = None) -> bytes:
        if self._eof:
            return b""

        if self._err:
            raise self._err

        try:
            if self._part_len - self._part_read_len == 0:
                header = await self._re.read_exactly(3)

                part_type = PartType(header[0])
                part_len = int.from_bytes(header[1:], byteorder="little")
                if part_type == PartType.NewPart:
                    self._next_part_callbak(header, False)
                    self._eof = True
                    return b""

                elif part_type == PartType.Data:
                    self._part_len = part_len
                    self._part_read_len = 0

                elif part_type == PartType.PartEOF:
                    self._next_part_callbak(None, False)
                    self._eof = True
                    return b""

                elif part_type == PartType.EOF:
                    self._next_part_callbak(None, True)
                    self._eof = True
                    return b""

                elif part_type == PartType.Error:
                    msg_bytes = await self._re.read_exactly(part_len)
                    msg = msg_bytes.decode()
                    err = ValueError(msg)
                    self._next_part_callbak(err, False)
                    self._err = err
                    raise err

                else:
                    err = ValueError(f"Invalid part type: {part_type}")
                    self._next_part_callbak(err, False)
                    self._err = err
                    raise err

            part_rest_len = self._part_len - self._part_read_len
            if n is None:
                n = part_rest_len
            elif n > part_rest_len:
                n = part_rest_len

            data = await self._re.read(n)
            if not data:
                err = ValueError("Unexpected EOF")
                self._next_part_callbak(err, False)
                self._err = err
                raise err

            self._part_read_len += len(data)
            return data

        except Exception as e:
            self._next_part_callbak(e, False)
            self._err = e
            raise


class ChunkedReader:
    def __init__(self, reader: ReadCloser):
        self._raw_reader = reader
        self._re = ReaderExt(reader)
        self._part_header: bytes | None = None
        self._err = None
        self._eof = False

    async def next_part(self) -> tuple[str, PartReader] | None:
        if self._eof:
            return None

        if self._err:
            raise self._err

        if self._part_header is None:
            self._part_header = await self._re.read_exactly(3)

        part_type = PartType(self._part_header[0])
        part_len = int.from_bytes(self._part_header[1:], byteorder="little")
        if part_type == PartType.NewPart:
            name_bytes = await self._re.read_exactly(part_len)
            name = name_bytes.decode()
            self._part_header = None

            return name, PartReader(self._re, self._next_part_callback)

        elif part_type == PartType.Data:
            raise ValueError("Unexpected data part")

        elif part_type == PartType.EOF:
            self._eof = True
            return None

        elif part_type == PartType.Error:
            msg_bytes = await self._re.read_exactly(part_len)
            msg = msg_bytes.decode()
            self._err = ValueError(msg)
            raise self._err

        else:
            raise ValueError(f"Invalid part type: {part_type}")

    async def next_data_part(self) -> tuple[str, bytes] | None:
        part = await self.next_part()
        if part is None:
            return None

        name, pr = part

        data = bytearray()
        while True:
            chunk = await pr.read(1024 * 4)
            if not chunk:
                break
            data.extend(chunk)

        return name, bytes(data)

    async def close(self):
        await self._raw_reader.close()

    def _next_part_callback(self, v: bytes | Exception | None, eof: bool):
        if eof:
            self._eof = True
            return

        if isinstance(v, Exception):
            self._err = v
            return

        if isinstance(v, bytes):
            self._part_header = v
            return


class PartWriter:
    def __init__(self, we: WriteCloser):
        self._we = we

    async def write(self, data: bytes) -> None:
        while len(data) > 0:
            wl = min(len(data), 0xFFFF)
            header = bytearray(3)
            header[0] = PartType.Data.value
            wl_bytes = wl.to_bytes(2, byteorder="little")
            header[1] = wl_bytes[0]
            header[2] = wl_bytes[1]
            await self._we.write(header)
            await self._we.write(data[:wl])
            data = data[wl:]

    async def send_part_eof(self) -> None:
        header = bytearray(3)
        header[0] = PartType.PartEOF.value
        await self._we.write(header)


class ChunkedWriter:
    def __init__(self, writer: WriteCloser):
        self._raw_writer = writer

    async def begin_part(self, name: str) -> PartWriter:
        header = bytearray(3)
        name_bytes = name.encode()
        header[0] = PartType.NewPart.value
        name_len_bytes = len(name_bytes).to_bytes(2, byteorder="little")
        header[1] = name_len_bytes[0]
        header[2] = name_len_bytes[1]
        await self._raw_writer.write(header)
        await self._raw_writer.write(name_bytes)

        return PartWriter(self._raw_writer)

    async def write_data_part(self, name: str, data: bytes) -> None:
        p = await self.begin_part(name)
        await p.write(data)
        await p.send_part_eof()

    async def write_stream_part(self, name: str, reader: Reader):
        p = await self.begin_part(name)
        while True:
            data = await reader.read(1024 * 4)
            if not data:
                break
            await p.write(data)

        await p.send_part_eof()

    async def send_error(self, msg: str):
        msg_bytes = msg.encode()

        buf = bytearray(3 + len(msg_bytes))
        buf[0] = PartType.Error.value
        msg_len_bytes = len(msg_bytes).to_bytes(2, byteorder="little")
        buf[1] = msg_len_bytes[0]
        buf[2] = msg_len_bytes[1]
        buf[3:] = msg_bytes

        await self._raw_writer.write(buf)

    async def send_eof(self):
        header = bytearray(3)
        header[0] = PartType.EOF.value
        await self._raw_writer.write(header)

    async def close(self):
        await self._raw_writer.close()
