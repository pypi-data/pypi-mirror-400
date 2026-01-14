from abc import (
    ABC,
    abstractmethod,
)


class Closer(ABC):
    @abstractmethod
    async def close(self) -> None: ...


class Reader(ABC):
    @abstractmethod
    async def read(self, n: int | None = None) -> bytes: ...


class Writer(ABC):
    @abstractmethod
    async def write(self, data: bytes) -> None: ...


class WriteCloser(Writer, Closer):
    pass


class ReadCloser(Reader, Closer):
    pass


class ReadWriter(Reader, Writer):
    pass


class ReadWriteCloser(ReadWriter, Closer):
    pass
