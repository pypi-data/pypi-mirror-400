# full_p2p_stream_test.py
import asyncio
import jwt
from time import time
from typing import Optional, List, Any

# Replace `streams_network` with your actual python package name built from pyo3
from streams_network import BootstrapNetwork, P2PNode

SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"


def create_jwt(owner: str, email: str, expires_in_seconds: int = 3600) -> str:
    payload = {
        "owner": owner,
        "email": email,
        "exp": time() + expires_in_seconds,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


class MyHandler:
    def on_message(self, peer_id: str, payload: bytes) -> bytes:
        print(f"[handler] on_message {peer_id[:12]} size {len(payload)}")
        return b"ACK"

    def on_response(self, peer_id: str, payload: bytes) -> None:
        print(f"[handler] on_response {peer_id[:12]} size {len(payload)}")

    def on_peer_connected(self, peer_id: str) -> None:
        print(f"[handler] peer connected {peer_id[:12]}")

    def on_peer_disconnected(self, peer_id: str) -> None:
        print(f"[handler] peer disconnected {peer_id[:12]}")

    def on_stream_message(self, peer_id: str, message: bytes) -> None:
        print(f"[handler] stream message from {peer_id[:12]} {len(message)} bytes")

    def on_stream_response(self, peer_id: str, message: bytes) -> None:
        print(f"[handler] stream response from {peer_id[:12]} {len(message)} bytes")


# helpers
async def send_stream_auto(
    sender: P2PNode,
    peer_id: str,
    data: bytes,
    chunk_size: int = 1024,
    delay: float = 0.005,
):
    """Send data in chunks from sender → peer"""
    await sender.start_stream(peer_id)
    for i in range(0, len(data), chunk_size):
        await sender.send_stream_message(peer_id, data[i : i + chunk_size])
        await asyncio.sleep(delay)
    await sender.close_stream(peer_id)


async def receive_stream_auto(
    receiver: P2PNode, peer_id: str, poll_interval: float = 0.02
) -> bytes:
    """Poll receiver until stream closes and return accumulated bytes."""
    collected = bytearray()
    while True:
        if await receiver.stream_ready(peer_id):
            batch = await receiver.get_stream_batch(peer_id)
            collected.extend(batch)
        await asyncio.sleep(poll_interval)
        active = await receiver.get_active_streams()
        # when the remote peer no longer has an active stream entry, we finish
        if peer_id not in active:
            # also fetch any leftover batch on close
            if await receiver.stream_ready(peer_id):
                collected.extend(await receiver.get_stream_batch(peer_id))
            break
    return bytes(collected)


async def wait_for_connected(node: P2PNode, timeout: float = 5.0):
    for _ in range(int(timeout / 0.1)):
        peers = await node.get_peers()
        if peers:
            return peers
        await asyncio.sleep(0.1)
    return []


async def main():
    token = create_jwt("user1", "user1@example.com")
    cfg1 = BootstrapNetwork(
        bearer_token=token, ip="127.0.0.1", port=0, owner="user1", bootstrap_url=""
    )
    cfg2 = BootstrapNetwork(
        bearer_token=token, ip="127.0.0.1", port=0, owner="user2", bootstrap_url=""
    )

    print("creating nodes...")
    node_a = await P2PNode.create(cfg1)
    node_b = await P2PNode.create(cfg2)

    print("listening ports:", node_a.listen_port(), node_b.listen_port())
    handler_a = MyHandler()
    handler_b = MyHandler()

    await node_a.start_event_loop(handler_a)
    await node_b.start_event_loop(handler_b)

    # Connect node_a -> node_b (dial b)
    peer_b = node_b.peer_id()
    port_b = node_b.listen_port()
    print("dialing:", peer_b, port_b)
    await node_a.connect(peer_b, "127.0.0.1", str(port_b))

    # wait for connection
    peers = await wait_for_connected(node_a, timeout=5.0)
    if not peers:
        print("No peers connected; aborting test.")
        return
    print("connected peers on A:", peers)

    target = peers[0]
    print("target peer:", target[:12])

    # prepare receiver side accumulation
    await node_b.start_stream(node_a.peer_id())

    # prepare data and run concurrent send + receive
    big_data = b"STREAM-DATA-" * 4096  # ~48KB
    print("sending bytes:", len(big_data))

    send_task = asyncio.create_task(
        send_stream_auto(node_a, target, big_data, chunk_size=2048)
    )
    recv_task = asyncio.create_task(receive_stream_auto(node_b, node_a.peer_id()))

    await send_task
    received = await recv_task

    print("received bytes:", len(received))
    print("integrity:", received == big_data)

    # cleanup
    await node_a.stop_event_loop()
    await node_b.stop_event_loop()


if __name__ == "__main__":
    asyncio.run(main())
