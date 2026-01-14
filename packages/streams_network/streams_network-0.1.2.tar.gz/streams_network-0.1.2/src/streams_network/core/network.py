import asyncio
import logging
from random import sample
from typing import List, Optional

from streams_network import P2PNode, Nodes, Node
from streams_network.core import Bootstrap
from streams_network.core.handler import DefaultHandler
from streams_network.utils.node_picker import pick_working_connection
from streams_network.core.protocol import DefaultProtocols

logger = logging.getLogger(__name__)


class Network:
    """
    High-level Python API over the Rust P2P node.

    Responsibilities:
    - Manage P2P node lifecycle
    - Expose messaging and stream APIs
    - Bridge Rust callbacks to DefaultHandler
    """

    def __init__(self, boot: Bootstrap):
        self.boot = boot
        self.handler = DefaultHandler()
        self.protocol = DefaultProtocols(self)
        self._node: Optional[P2PNode] = None
        self._running: bool = False
        self._keepalive_task: Optional[asyncio.Task] = None



    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def _require_node(self) -> P2PNode:
        if self._node is None:
            raise RuntimeError("Network is not started. Call start() first.")
        return self._node

    async def get_node(self) -> P2PNode:
        if self._node is None:
            self._node = await P2PNode.create(self.boot.config)
        return self._node

    async def start(self) -> None:
        if self._running:
            return

        node = await self.get_node()
        await node.start_event_loop(self.handler)
        await node.start_event_loop(self.protocol)
        await self.protocol.initialize()

        self._running = True
        self._keepalive_task = asyncio.create_task(self._keepalive())

        logger.info("Network started")

    async def stop(self) -> None:
        self._running = False

        if self._keepalive_task:
            self._keepalive_task.cancel()
            self._keepalive_task = None

        if self._node:
            await self._node.stop_event_loop()
            self._node = None

        logger.info("Network stopped")

    async def _keepalive(self) -> None:
        while self._running:
            try:
                node = await self._require_node()
                peers = await node.get_peers()

                for peer_id in peers:
                    await node.send_message(peer_id, b"PING")

            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.debug("Keepalive error: %s", exc)

            await asyncio.sleep(10)

    # ------------------------------------------------------------------
    # Peer management
    # ------------------------------------------------------------------

    async def discover(self) -> Nodes:
        node = await self._require_node()
        return await node.peer_discover()

    async def get_peers(self) -> List[str]:
        node = await self._require_node()
        return await node.get_peers()

    async def get_remote_peers(self) -> List[str]:
        peers = await self.get_peers()
        return [p for p in peers if p != self.boot.peer_id]

    async def get_random_peers(self, k: int = 3) -> List[str]:
        peers = await self.get_peers()
        if not peers:
            return []

        return sample(peers, min(k, len(peers)))


    async def direct_connect(self, peer_id: str, ip: str, port: int, transport: str) -> None:
        node = await self._require_node()
        await node.connect(peer_id, ip, str(port))
        
        asyncio.create_task(self.protocol.handshake_with_peer(peer_id))
        return ip, port, transport

    async def connect(self, node_info: Node) -> None:
        resp = await pick_working_connection(node_info.connections)
        if resp is None:
            logger.debug(
                "No working connection for peer %s",
                node_info.node_id[:12],
            )
            return

        ip, port, transport = resp
        await self.direct_connect(node_info.node_id, ip, port, transport)

        return ip, port, transport

    # ------------------------------------------------------------------
    # Messaging
    # ------------------------------------------------------------------

    async def send(self, peer_id: str, payload: bytes) -> None:
        node = await self._require_node()
        await node.send_message(peer_id, payload)

    async def broadcast(self, payload: bytes) -> None:
        node = await self._require_node()
        await node.broadcast(payload)

    # ------------------------------------------------------------------
    # Streams (thin proxy)
    # ------------------------------------------------------------------

    async def start_stream(self, peer_id: str) -> None:
        node = await self._require_node()
        await node.start_stream(peer_id)

    async def send_stream_message(self, peer_id: str, data: bytes) -> None:
        node = await self._require_node()
        await node.send_stream_message(peer_id, data)

    async def close_stream(self, peer_id: str) -> None:
        node = await self._require_node()
        await node.close_stream(peer_id)

    async def get_active_streams(self):
        node = await self._require_node()
        return await node.get_active_streams()

    async def stream_ready(self, peer_id: str):
        node = await self._require_node()
        return await node.stream_ready(peer_id)

    async def get_stream_batch(self, peer_id: str):
        node = await self._require_node()
        return await node.get_stream_batch(peer_id)
