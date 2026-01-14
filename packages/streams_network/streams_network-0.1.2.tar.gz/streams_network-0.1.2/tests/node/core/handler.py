# core/handler.py
import logging

logger = logging.getLogger("Handler")
logger.setLevel(logging.INFO)


class MyHandler:
    def on_message(self, peer_id: str, payload: bytes) -> bytes:
        logger.info(f"📨 MSG  {peer_id[:12]} → {payload.decode(errors='ignore')}")
        return b"ACK"

    def on_response(self, peer_id: str, payload: bytes) -> None:
        logger.info(f"📬 RESP {peer_id[:12]} → {payload.decode(errors='ignore')}")

    def on_peer_connected(self, peer_id: str) -> None:
        logger.info(f"✅ CONNECTED {peer_id[:12]}")

    def on_peer_disconnected(self, peer_id: str) -> None:
        logger.info(f"❌ DISCONNECTED {peer_id[:12]}")

    # 🔥 ASIL OLAY
    def on_stream_message(self, peer_id: str, message: bytes) -> None:
        logger.info(f"🌊 STREAM IN {peer_id[:12]} → {len(message)} bytes")

    def on_stream_closed(self, peer_id: str) -> None:
        logger.info(f"🧨 STREAM CLOSED {peer_id[:12]}")
