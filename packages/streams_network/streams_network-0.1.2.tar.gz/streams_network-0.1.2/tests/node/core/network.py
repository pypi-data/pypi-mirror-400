# core/network.py
import asyncio
import logging
from typing import Optional, List

from streams_network import P2PNode, Nodes
from core import Bootstrap

logger = logging.getLogger("Network")
logger.setLevel(logging.DEBUG)


class Network:
    def __init__(self, boot: Bootstrap):
        self.boot = boot
        self._node: Optional[P2PNode] = None
        self._port: int = 0
        self.handler = None
        self._running = False

    async def get_node(self) -> P2PNode:
        if self._node is None:
            self._node = await P2PNode.create(self.boot.config)
        return self._node

    async def start(self) -> None:
        if self._running:
            return

        if not self.handler:
            raise RuntimeError("Handler is not defined")

        node = await self.get_node()
        await node.start_event_loop(self.handler)
        self._running = True

        # keepalive sadece MESSAGE için, stream'e dokunmaz
        asyncio.create_task(self._keepalive())

    async def _keepalive(self):
        while self._running:
            try:
                peers = await self.get_peers()
                for p in peers:
                    await self._node.send_message(p, b"PING")
            except Exception:
                pass
            await asyncio.sleep(10)

    async def stop(self) -> None:
        self._running = False
        if self._node:
            await self._node.stop_event_loop()

    # ---------- BASIC ----------
    async def discover(self) -> Nodes:
        return await self._node.peer_discover()

    async def connect(self, peer_id: str, ip: str, port) -> None:
        await self._node.connect(peer_id, ip, str(port))

    async def get_peers(self) -> List[str]:
        return await self._node.get_peers()

    async def get_remote_peers(self) -> List[str]:
        peers = await self.get_peers()
        return [p for p in peers if p != self.boot.peer_id]

    async def send(self, peer_id: str, payload: bytes):
        await self._node.send_message(peer_id, payload)

    async def broadcast(self, payload: bytes):
        await self._node.broadcast(payload)

    # ---------- STREAM (DÜMDÜZ PROXY) ----------
    async def start_stream(self, peer_id: str):
        await self._node.start_stream(peer_id)

    async def send_stream_message(self, peer_id: str, data: bytes):
        await self._node.send_stream_message(peer_id, data)

    async def close_stream(self, peer_id: str):
        await self._node.close_stream(peer_id)

    async def get_active_streams(self):
        return await self._node.get_active_streams()

    async def stream_ready(self, peer_id: str):
        return await self._node.stream_ready(peer_id)

    async def get_stream_batch(self, peer_id: str):
        return await self._node.get_stream_batch(peer_id)
