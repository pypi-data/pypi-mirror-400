"""
Fixed P2P network test with comprehensive debugging
"""

import asyncio
import jwt
from time import time
from streams_network import BootstrapNetwork, P2PNode

# --- Token generation ---
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"


def create_jwt(owner: str, email: str, expires_in_seconds: int = 3600) -> str:
    payload = {"owner": owner, "email": email, "exp": time() + expires_in_seconds}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


# --- Message handler ---
class MyHandler:
    """Message handler implementing required callbacks"""

    def on_message(self, peer_id: str, payload: bytes) -> bytes:
        print(f"📨 Received message from {peer_id[:20]}: {payload.decode()}")
        return b"ACK: " + payload

    def on_response(self, peer_id: str, payload: bytes) -> None:
        print(f"📬 Response from {peer_id[:20]}: {payload.decode()}")

    def on_peer_connected(self, peer_id: str) -> None:
        print(f"✅ Peer connected: {peer_id[:20]}")

    def on_peer_disconnected(self, peer_id: str) -> None:
        print(f"❌ Peer disconnected: {peer_id[:20]}")

    def on_stream_message(self, peer_id: str, message: bytes):
        print(f"📥 Stream message from {peer_id[:20]}: {message.decode()}")

    def on_stream_response(self, peer_id: str, message: bytes):
        print(f"📤 Stream response from {peer_id[:20]}: {message.decode()}")


async def main_with_background_loop():
    """Run event loop in background with comprehensive debugging"""

    # 1. Create JWT token
    token = create_jwt(
        owner="user1", email="user1@example.com", expires_in_seconds=3600
    )
    print(f"🔑 Generated JWT token")

    # 2. Create configuration
    config = BootstrapNetwork(
        bearer_token=token,
        ip="127.0.0.1",
        owner="user1",
        port=0,
        bootstrap_url="http://127.0.0.1:8000",
    )

    peer_id = config.get_peer_id()
    print(f"🔑 My Peer ID: {peer_id}")

    # 3. Create P2P node
    node = await P2PNode.create(config)
    listen_port = node.listen_port()
    print(f"🌐 Listening on port: {listen_port}")

    # 4. Start background event loop FIRST
    handler = MyHandler()
    await node.start_event_loop(handler)
    print("🔄 Event loop started in background")

    # 5. Wait longer for event loop to initialize
    print("⏳ Waiting for event loop to initialize...")
    await asyncio.sleep(2)

    # 6. Discover peers
    print("🔍 Discovering peers...")
    nodes = await node.peer_discover()
    print(f"🔍 Discovered {len(nodes.nodes)} peers")

    if len(nodes.nodes) == 0:
        print("⚠️  No peers discovered. Make sure bootstrap server is running.")

    for node_info in nodes.nodes:
        print(f"   - Peer: {node_info.node_id[:20]}")
        print(f"     Owner: {node_info.owner}")
        print(f"     Address: {node_info.ip}:{node_info.port}")

    # 7. Connect to discovered peers
    if len(nodes.nodes) > 0:
        print("\n🔗 Attempting to connect to peers...")
        for peer in nodes.nodes:
            if peer.node_id != peer_id:
                try:
                    print(
                        f"   ↪ Connecting to {peer.node_id[:20]} at {peer.ip}:{peer.port}"
                    )
                    await node.connect(peer.node_id, peer.ip, peer.port)
                    print(f"   ✓ Connect initiated for {peer.node_id[:20]}")
                except Exception as e:
                    print(
                        f"   ✗ Failed to initiate connection to {peer.node_id[:20]}: {e}"
                    )

    # 8. Wait longer for connections to establish
    print("\n⏳ Waiting for connections to establish...")
    for i in range(5):
        await asyncio.sleep(1)
        connected = await node.get_peers()
        print(f"   [{i+1}/5] Connected peers: {len(connected)}")
        if len(connected) > 0:
            break

    # 9. Check final connected peers
    connected = await node.get_peers()
    print(f"\n✅ Finally connected to {len(connected)} peers")
    for peer in connected:
        print(f"   - {peer[:20]}")

    # 10. Send messages to connected peers
    if connected:
        print("\n📤 Testing message sending...")
        target_peer = connected[0]
        print(f"   Sending to {target_peer[:20]}...")
        try:
            await node.send_message(target_peer, b"Hello from Python!")
            print(f"   ✓ Message sent successfully")
        except Exception as e:
            print(f"   ✗ Failed to send message: {e}")

        await asyncio.sleep(1)  # Wait for response
    else:
        print("\n⚠️  No connected peers to send messages to")

    # 11. Broadcast test
    if len(connected) > 0:
        print("\n📡 Testing broadcast...")
        try:
            await node.broadcast(b"Broadcasting to everyone!")
            print(f"   ✓ Broadcast sent to {len(connected)} peers")
        except Exception as e:
            print(f"   ✗ Broadcast failed: {e}")

        await asyncio.sleep(1)  # Wait for responses

    # 12. Keep running for a while to receive messages
    print("\n🎧 Listening for messages (Ctrl+C to exit)...")
    print(f"   You can now start another instance and they should connect")
    try:
        while True:
            broadcast_chat = input(
                "💬 Enter message to broadcast (or 'exit' to quit): "
            )
            if broadcast_chat.lower() == "exit":
                break
            await node.broadcast(broadcast_chat.encode())
            await asyncio.sleep(0.03)  # Small delay
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    finally:
        await node.stop_event_loop()
        print("👋 Event loop stopped")


if __name__ == "__main__":
    asyncio.run(main_with_background_loop())
