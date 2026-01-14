from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from .abc import IMuxedStream
from ..io import ReadWriterExt

MAGIC_NUMBER = 0xC0DE9CCE
VERSION = 1


@dataclass
class ClientHelloPacket:
    magic_number: int
    version: int
    job_set_id: str
    local_job_id: str
    salt: bytes

    async def to_stream(self, rwe: ReadWriterExt):
        await rwe.write_u32_be(self.magic_number)
        await rwe.write_u8(self.version)
        await rwe.write_string_u8(self.job_set_id)
        await rwe.write_string_u8(self.local_job_id)
        await rwe.write(self.salt)


class PacketType(Enum):
    RPC_REQ = 0x01
    RPC_RESP = 0x02
    OPEN_STREAM = 0x03
    STREAM_OPENING = 0x04
    STREAM_RESULT = 0x05


class Packet(ABC):
    @classmethod
    @abstractmethod
    def packet_type(cls) -> PacketType: ...

    @abstractmethod
    async def to_stream(self, rwe: ReadWriterExt): ...

    @classmethod
    @abstractmethod
    async def from_stream(cls, rwe: ReadWriterExt): ...


@dataclass
class RpcRequestPacket(Packet):
    path: str

    @classmethod
    def packet_type(cls) -> PacketType:
        return PacketType.RPC_REQ

    async def to_stream(self, rwe: ReadWriterExt):
        await rwe.write_string_u8(self.path)

    @classmethod
    async def from_stream(cls, rwe: ReadWriterExt):
        self = cls(path="")
        self.path = await rwe.read_string_u8()
        return self


@dataclass
class RpcResponsePacket(Packet):
    code: str

    @classmethod
    def packet_type(cls) -> PacketType:
        return PacketType.RPC_RESP

    async def to_stream(self, rwe: ReadWriterExt):
        await rwe.write_string_u8(self.code)

    @classmethod
    async def from_stream(cls, rwe: ReadWriterExt):
        self = cls(code="")
        self.code = await rwe.read_string_u8()
        return self


@dataclass
class OpenStreamPacket(Packet):
    timeout_sec: int
    dst_job_id: str
    name: str

    @classmethod
    def packet_type(cls) -> PacketType:
        return PacketType.OPEN_STREAM

    async def to_stream(self, rwe: ReadWriterExt):
        await rwe.write_u8(self.timeout_sec)
        await rwe.write_string_u8(self.dst_job_id)
        await rwe.write_string_u8(self.name)

    @classmethod
    async def from_stream(cls, rwe: ReadWriterExt):
        self = cls(timeout_sec=0, dst_job_id="", name="")
        self.timeout_sec = await rwe.read_u8()
        self.dst_job_id = await rwe.read_string_u8()
        self.name = await rwe.read_string_u8()
        return self


@dataclass
class StreamOpeningPacket(Packet):
    timeout_sec: int
    src_job_id: str
    name: str

    @classmethod
    def packet_type(cls) -> PacketType:
        return PacketType.STREAM_OPENING

    async def to_stream(self, rwe: ReadWriterExt):
        await rwe.write_u8(self.timeout_sec)
        await rwe.write_string_u8(self.src_job_id)
        await rwe.write_string_u8(self.name)

    @classmethod
    async def from_stream(cls, rwe: ReadWriterExt):
        self = cls(timeout_sec=0, src_job_id="", name="")
        self.timeout_sec = await rwe.read_u8()
        self.src_job_id = await rwe.read_string_u8()
        self.name = await rwe.read_string_u8()
        return self


class StreamResultCode(Enum):
    OK = 0
    UNKNOWN_ERROR = 1
    TIMEOUT = 2
    NOTFOUND = 3


@dataclass
class StreamResultPacket(Packet):
    code: StreamResultCode

    @classmethod
    def packet_type(cls) -> PacketType:
        return PacketType.STREAM_RESULT

    async def to_stream(self, rwe: ReadWriterExt):
        await rwe.write_u8(self.code.value)

    @classmethod
    async def from_stream(cls, rwe: ReadWriterExt):
        self = cls(code=StreamResultCode.OK)
        self.code = StreamResultCode(await rwe.read_u8())
        return self


class JobStream:
    def __init__(
            self, peer_job_id: str, name: str, raw_str: IMuxedStream, rwe: ReadWriterExt
    ):
        self._peer_job_id = peer_job_id
        self._name = name
        self._raw_str = raw_str
        self._rwe = rwe

    def peer_job_id(self) -> str:
        return self._peer_job_id

    def name(self) -> str:
        return self._name

    async def read(self, max_bytes: int | None = None):
        return await self._rwe.read(max_bytes)

    async def write(self, data: bytes):
        await self._rwe.write(data)

    async def close(self):
        await self._raw_str.close()


class CodeError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message

    def __str__(self):
        return f"{self.code}: {self.message}"
