from contextlib import asynccontextmanager
import logging
import os
import trio
from noise.connection import NoiseConnection, Keypair
from argon2.low_level import hash_secret_raw, Type

import jcclang.core.io as io
from jcclang.core.io.ext import ReadWriteCloserExt, ReadWriterExt
from jcclang.core.io.chunked import ChunkedReader, ChunkedWriter
from .exceptions import OpenJobStreamError
from .types import (
    MAGIC_NUMBER,
    VERSION,
    ClientHelloPacket,
    CodeError,
    JobStream,
    OpenStreamPacket,
    PacketType,
    RpcResponsePacket,
    StreamOpeningPacket,
    StreamResultCode,
    StreamResultPacket,
)
from .abc import IMuxedStream
from .yamux import Yamux
from .utils import MuxStreamReadWriter, NoiseConn

logger = logging.getLogger("jcclang.core.jobhub")


class RPCResponseReader:
    def __init__(self, rwe: ReadWriteCloserExt):
        self._rwe = rwe

    async def get(self) -> ChunkedReader | CodeError:
        pkt_type = await self._rwe.read_u8()
        if pkt_type != PacketType.RPC_RESP.value:
            return CodeError(
                "InvalidPacketType",
                f"Expected {PacketType.RPC_RESP}, got {pkt_type}",
            )

        resp = await RpcResponsePacket.from_stream(self._rwe)
        cr = ChunkedReader(self._rwe)
        if resp.code == "OK":
            return cr

        p = await cr.next_data_part()
        if p is None:
            return CodeError("NoData", "No data received")
        else:
            await cr.close()
            return CodeError(resp.code, p[1].decode())

    async def close(self):
        await self._rwe.close()


class JobHubClient:
    def __init__(
        self,
        mux_conn: Yamux,
        nursery: trio.Nursery,
    ):
        self._mux_conn = mux_conn
        self._nursery = nursery
        self._pending_strs: dict[str, set[JobStream]] = {}
        self._pending_str_event = trio.Event()
        self._closed = False

    @classmethod
    @asynccontextmanager
    async def connect(
        cls,
        host: str,
        port: int,
        job_set_id: str,
        local_job_id: str,
        shared_secret: bytes,
    ):

        # 1. 建立 TCP 连接
        con = await trio.open_tcp_stream(host, int(port))
        rwe = ReadWriterExt.from_stream(con)

        # 2. 发送 ClientHelloPacket
        salt = os.urandom(32)
        cli_hello_pkt = ClientHelloPacket(
            magic_number=MAGIC_NUMBER,
            version=VERSION,
            job_set_id=job_set_id,
            local_job_id=local_job_id,
            salt=salt,
        )
        await cli_hello_pkt.to_stream(rwe)

        # 3. 生成 PSK
        psk = hash_secret_raw(
            time_cost=1,
            memory_cost=4 * 1024,
            parallelism=1,
            hash_len=32,
            type=Type.ID,
            secret=shared_secret,
            salt=salt,
        )

        # 4. 初始化 Noise XX + PSK 握手
        noise = NoiseConnection.from_name(b"Noise_XXpsk0_25519_ChaChaPoly_BLAKE2s")
        priv = os.urandom(32)
        noise.set_keypair_from_private_bytes(Keypair.STATIC, priv)
        noise.set_as_initiator()
        noise.set_psks(psk)
        noise.start_handshake()

        # --- 握手第 1 消息 ---
        msg = noise.write_message()
        await rwe.write_u16_be(len(msg))
        await rwe.write(msg)

        # --- 接收第 1 响应 ---
        frame_len = await rwe.read_u16_be()
        frame = await rwe.read_exactly(frame_len)
        noise.read_message(frame)

        # --- 发送第 2 消息，完成握手 ---
        msg = noise.write_message()
        await rwe.write_u16_be(len(msg))
        await rwe.write(msg)

        noise_conn = NoiseConn(con, rwe, True, noise.encrypt, noise.decrypt)

        mux_conn = Yamux(noise_conn, True)

        async with trio.open_nursery() as nursery:
            cli = cls(mux_conn, nursery)
            nursery.start_soon(mux_conn.start)
            nursery.start_soon(cli._handle_incoming)

            yield cli

            await cli._close()
            await mux_conn.close()
            await noise_conn.close()
            nursery.cancel_scope.cancel()

    async def nursery(self):
        return self._nursery

    async def accept_stream(self, name: str = ""):
        while not self._closed:
            pstrs = self._pending_strs.get(name)
            if pstrs is not None and len(pstrs) > 0:
                str = pstrs.pop()
                if len(pstrs) == 0:
                    del self._pending_strs[name]

                pkt = StreamResultPacket(code=StreamResultCode.OK)
                try:
                    await str._rwe.write_u8(pkt.packet_type().value)
                    await pkt.to_stream(str._rwe)
                    return str
                except:
                    await str.close()
                    raise

            await self._pending_str_event.wait()
            self._pending_str_event = trio.Event()
        raise trio.ClosedResourceError("client closed")

    async def open_stream(self, dst_job_id: str, name: str = "", timeout_sec: int = 15):
        raw_str = await self._mux_conn.open_stream()
        rwe = ReadWriterExt(MuxStreamReadWriter(raw_str))

        try:
            pkt = OpenStreamPacket(
                timeout_sec=timeout_sec, dst_job_id=dst_job_id, name=name
            )
            await rwe.write_u8(pkt.packet_type().value)
            await pkt.to_stream(rwe)

            pkt_type = await rwe.read_u8()
            if pkt_type != PacketType.STREAM_RESULT.value:
                await raw_str.close()
                raise ValueError(f"Expected STREAM_RESULT, got {pkt_type}")

            result = await StreamResultPacket.from_stream(rwe)
            if result.code == StreamResultCode.OK:
                str = JobStream(dst_job_id, name, raw_str, rwe)
                return str
            else:
                await raw_str.close()
                raise OpenJobStreamError(result.code)
        except:
            await raw_str.close()
            raise

    async def do_rpc(self, path: str) -> tuple[ChunkedWriter, RPCResponseReader]:
        str = await self._mux_conn.open_stream()
        rw = MuxStreamReadWriter(str)
        rwe = ReadWriteCloserExt(rw)

        try:
            await rwe.write_u8(PacketType.RPC_REQ.value)
            await rwe.write_string_u8(path)

            return ChunkedWriter(io.NoopWriteCloser(rw)), RPCResponseReader(rwe)
        except:
            await str.close()
            raise

    async def _close(self):
        self._closed = True
        self._pending_str_event.set()

    async def _handle_incoming(self):
        try:
            while True:
                str = await self._mux_conn.accept_stream()
                rwe = ReadWriterExt(MuxStreamReadWriter(str))

                try:
                    type = await rwe.read_u8()
                    if type == PacketType.STREAM_OPENING.value:
                        pkt = await StreamOpeningPacket.from_stream(rwe)
                        self._nursery.start_soon(
                            self._handle_open_stream, str, rwe, pkt
                        )

                    else:
                        raise ValueError(f"Unknown packet type: {type}")

                except Exception as e:
                    logger.warning(f"Read packet: {e}")
                    continue

        except Exception as e:
            logger.warning(f"Handle incoming: {e}")
            return

    async def _handle_open_stream(
        self, str: IMuxedStream, rwe: ReadWriterExt, pkt: StreamOpeningPacket
    ):
        logger.debug(
            f"Stream {pkt.name} opening, src: {pkt.src_job_id}, timeout: {pkt.timeout_sec}"
        )

        js = JobStream(pkt.src_job_id, pkt.name, str, rwe)
        self._pending_strs.setdefault(pkt.name, set()).add(js)

        self._pending_str_event.set()

        # 等待超时

        await trio.sleep(pkt.timeout_sec)

        pstrs = self._pending_strs.get(pkt.name)
        if pstrs is not None and js in pstrs:
            try:
                ret = StreamResultPacket(code=StreamResultCode.TIMEOUT)
                await rwe.write_u8(ret.packet_type().value)
                await ret.to_stream(rwe)
            finally:
                pass

            await js.close()

            pstrs.remove(js)
            if len(pstrs) == 0:
                del self._pending_strs[pkt.name]
