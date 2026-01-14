# core/protocol.py

import asyncio
import logging
from typing import Optional
from uuid import uuid4
from streams_network.models import HelloMessage  # Network'ü buradan import edeceğiz

logger = logging.getLogger(__name__)


class DefaultProtocols:
    """
    Core control-plane protocols (handshake, topic discovery, etc.)
    """

    def __init__(self, network):
        from streams_network.core.network import Network, P2PNode
        self.network: Network = network
        self.boot = network.boot
        self.node: P2PNode = None  
        
    async def initialize(self):
        self.node = await self.network.get_node()

    async def handshake_with_peer(self, peer_id: str):
        
        if not self.node:
            logger.warning("Node not ready for handshake")
            return

        msg = HelloMessage(
            msg_id=uuid4().hex,
            peer_id=self.node.peer_id,
            owner=self.boot.email,
            connection=self.boot.config.connections
        )

        try:
            await asyncio.sleep(1)
            await self.network.send(peer_id, msg.to_json().encode())
            logger.info("Handshake sent to peer %s", peer_id[:12])
        except Exception as exc:
            logger.debug("Handshake failed to %s: %s", peer_id[:12], exc)
