from abc import (
    ABC,
    abstractmethod,
)

from types import (
    TracebackType,
)
from typing import (
    AsyncContextManager,
    Callable,
)


import trio

from jcclang.core.io.abc import ReadWriteCloser


# -------------------------- raw_connection interface.py --------------------------


class IRawConnection(ReadWriteCloser):
    """
    Interface for a raw connection.

    This interface provides a basic reader/writer connection abstraction.

    Attributes
    ----------
    is_initiator (bool):
        True if the local endpoint initiated
        the connection.

    """

    is_initiator: bool


# -------------------------- stream_muxer abc.py --------------------------


class IMuxedConn(ABC):
    """
    Interface for a multiplexed connection.

    References
    ----------
    https://github.com/libp2p/go-stream-muxer/blob/master/muxer.go

    Attributes
    ----------
    peer_id (ID):
        The identifier of the connected peer.
    event_started (trio.Event):
        An event that signals when the multiplexer has started.

    """

    event_started: trio.Event

    @abstractmethod
    def __init__(
        self,
        conn: IRawConnection,
    ) -> None:
        """
        Initialize a new multiplexed connection.

        :param conn: An instance of a secure connection used for new
            multiplexed streams.
        :param peer_id: The peer ID associated with the connection.
        """

    @property
    @abstractmethod
    def is_initiator(self) -> bool:
        """
        Determine if this connection is the initiator.

        :return: True if this connection initiated the connection,
            otherwise False.
        """

    @abstractmethod
    async def start(self) -> None:
        """
        Start the multiplexer.

        """

    @abstractmethod
    async def close(self) -> None:
        """
        Close the multiplexed connection.

        """

    @property
    @abstractmethod
    def is_closed(self) -> bool:
        """
        Check if the connection is fully closed.

        :return: True if the connection is closed, otherwise False.
        """

    @abstractmethod
    async def open_stream(self) -> "IMuxedStream":
        """
        Create and open a new multiplexed stream.

        :return: A new instance of IMuxedStream.
        """

    @abstractmethod
    async def accept_stream(self) -> "IMuxedStream":
        """
        Accept a new multiplexed stream initiated by the remote peer.

        :return: A new instance of IMuxedStream.
        """


class IMuxedStream(ReadWriteCloser, AsyncContextManager["IMuxedStream"]):
    """
    Interface for a multiplexed stream.

    Represents a stream multiplexed over a single connection.

    Attributes
    ----------
    muxed_conn (IMuxedConn):
        The underlying multiplexed connection.

    """

    muxed_conn: IMuxedConn

    @abstractmethod
    async def reset(self) -> None:
        """
        Reset the stream.

        This method closes both ends of the stream, instructing the remote
        side to hang up.
        """

    @abstractmethod
    def set_deadline(self, ttl: int) -> bool:
        """
        Set a deadline for the stream.

        :param ttl: Time-to-live for the stream in seconds.
        :return: True if the deadline was set successfully,
            otherwise False.
        """

    @abstractmethod
    async def __aenter__(self) -> "IMuxedStream":
        """Enter the async context manager."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit the async context manager and close the stream."""
        await self.close()


IEncrypter = Callable[[bytes], bytes]
IDecrypter = Callable[[bytes], bytes]
