#core/handler.py
import asyncio
import logging
from collections import defaultdict
from typing import DefaultDict, List

logger = logging.getLogger(__name__)


class DefaultHandler:
    """
    Default protocol handler.

    Responsibilities:
    - Dispatch control-plane messages to registered queues
    - Handle framed binary stream messages
    - Notify peer connection lifecycle events
    """

    def __init__(self) -> None:
        self.on_message_queues: List[asyncio.Queue] = []
        self.on_response_queues: List[asyncio.Queue] = []
        self.on_peer_connected_queues: List[asyncio.Queue] = []
        self.on_peer_disconnected_queues: List[asyncio.Queue] = []
        self.on_stream_message_queues: List[asyncio.Queue] = []
        self.on_stream_closed_queues: List[asyncio.Queue] = []

        self.stream_buffers: DefaultDict[str, bytes] = defaultdict(bytes)

        logger.info("DefaultHandler initialized")

    # ------------------------------------------------------------------
    # Control-plane callbacks
    # ------------------------------------------------------------------

    def on_message(self, peer_id: str, payload: bytes) -> bytes:
        """
        Called when a control message is received.
        Dispatches the message to all registered queues.
        """
        for queue in self.on_message_queues:
            try:
                queue.put_nowait((peer_id, payload))
            except Exception as exc:
                logger.debug(
                    "Failed to enqueue message from %s: %s",
                    peer_id[:12],
                    exc,
                )

        return b"ACK"

    def on_response(self, peer_id: str, payload: bytes) -> None:
        for queue in self.on_response_queues:
            try:
                queue.put_nowait((peer_id, payload))
            except Exception:
                pass

    def on_peer_connected(self, peer_id: str) -> None:
        for queue in self.on_peer_connected_queues:
            try:
                queue.put_nowait(peer_id)
            except Exception:
                pass

    def on_peer_disconnected(self, peer_id: str) -> None:
        for queue in self.on_peer_disconnected_queues:
            try:
                queue.put_nowait(peer_id)
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Stream handling (length-prefixed framing)
    # ------------------------------------------------------------------

    def on_stream_message(self, peer_id: str, message: bytes) -> None:
        """
        Handles framed stream messages.

        Frame format:
            [2 bytes length][payload]
        """
        buffer = self.stream_buffers[peer_id] + message

        while len(buffer) >= 2:
            length = int.from_bytes(buffer[:2], "big")
            if len(buffer) < 2 + length:
                break

            payload = buffer[2 : 2 + length]
            buffer = buffer[2 + length :]

            for queue in self.on_stream_message_queues:
                try:
                    queue.put_nowait((peer_id, payload))
                except Exception:
                    pass

        self.stream_buffers[peer_id] = buffer

    def on_stream_closed(self, peer_id: str) -> None:
        self.stream_buffers.pop(peer_id, None)

        for queue in self.on_stream_closed_queues:
            try:
                queue.put_nowait(peer_id)
            except Exception:
                pass
