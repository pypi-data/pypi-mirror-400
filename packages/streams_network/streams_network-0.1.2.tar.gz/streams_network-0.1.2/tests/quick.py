"""
FULL P2P STREAM TEST
- normal message
- raw stream
- chunked stream
- integrity check
"""

import asyncio
import jwt
from time import time
from streams_network import BootstrapNetwork, P2PNode


# ───────────────── TOKEN ─────────────────

SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"


def create_jwt(owner: str, email: str, expires_in_seconds: int = 3600) -> str:
    payload = {
        "owner": owner,
        "email": email,
        "exp": time() + expires_in_seconds,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# ───────────────── HANDLER ─────────────────


class MyHandler:
    def on_message(self, peer_id: str, payload: bytes) -> bytes:
        print(f"📨 MSG  {peer_id[:12]} → {payload.decode(errors='ignore')}")
        return b"ACK"

    def on_response(self, peer_id: str, payload: bytes) -> None:
        print(f"📬 RESP {peer_id[:12]} → {payload.decode(errors='ignore')}")

    def on_peer_connected(self, peer_id: str) -> None:
        print(f"✅ CONNECTED {peer_id[:12]}")

    def on_peer_disconnected(self, peer_id: str) -> None:
        print(f"❌ DISCONNECTED {peer_id[:12]}")

    def on_stream_message(self, peer_id: str, message: bytes) -> None:
        print(f"🌊 STREAM IN  {peer_id[:12]} → {len(message)} bytes")

    def on_stream_response(self, peer_id: str, message: bytes) -> None:
        print(f"🌊 STREAM RESP {peer_id[:12]} → {len(message)} bytes")


# ───────────────── STREAM HELPERS ─────────────────


async def send_stream_auto(
    node: P2PNode,
    peer_id: str,
    data: bytes,
    chunk_size: int = 2048,
):
    await node.start_stream(peer_id)

    for i in range(0, len(data), chunk_size):
        await node.send_stream_message(peer_id, data[i : i + chunk_size])
        await asyncio.sleep(0.005)

    # sadece kapat, veri bekleme
    await node.close_stream(peer_id)


async def receive_stream_auto(
    node: P2PNode,
    peer_id: str,
    poll_interval: float = 0.05,
) -> bytes:
    """Poll stream buffer until closed"""
    collected = bytearray()

    while True:
        if await node.stream_ready(peer_id):
            batch = await node.get_stream_batch(peer_id)
            collected.extend(batch)

        await asyncio.sleep(poll_interval)

        active = await node.get_active_streams()
        if peer_id not in active:
            break

    return bytes(collected)


# ───────────────── MAIN ─────────────────


async def main():
    token = create_jwt("user1", "user1@example.com")

    config = BootstrapNetwork(
        bearer_token=token,
        ip="127.0.0.1",
        port=0,
        owner="user1",
        bootstrap_url="http://127.0.0.1:8000",
    )

    print("🔑 Peer ID:", config.get_peer_id())

    node = await P2PNode.create(config)
    print("🌐 Listening on:", node.listen_port())

    handler = MyHandler()
    await node.start_event_loop(handler)
    await asyncio.sleep(2)

    # Discover & connect
    nodes = await node.peer_discover()
    for peer in nodes.nodes:
        if peer.node_id != config.get_peer_id():
            try:
                await node.connect(peer.node_id, peer.ip, peer.port)
            except Exception as e:
                print(f"⚠️ Failed to connect to {peer.node_id}: {e}")

    # Wait for connection
    for _ in range(10):
        peers = await node.get_peers()
        if peers:
            break
        await asyncio.sleep(1)

    peers = await node.get_peers()
    if not peers:
        print("⚠️ No peers connected")

    target = peers[0]
    print("🎯 Target peer:", target[:12])

    # ───── NORMAL MESSAGE ─────
    await node.send_message(target, b"Hello normal message")
    await asyncio.sleep(1)

    # ───── STREAM TEST ─────
    print("\n🚀 STREAM TEST")

    big_data = b"STREAM-DATA-" * 4096  # ~48KB
    print("📦 Sending bytes:", len(big_data))

    received = await send_stream_auto(node, target, big_data)
    if received is None:
        received = b""
    print("📥 Received bytes:", len(received))
    print("✅ Integrity:", received == big_data)

    print("\n🎉 ALL TESTS COMPLETED")
    print("Ctrl+C to exit")

    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
