# main.py
import os
import asyncio
import logging
from core import create_jwt, Bootstrap, Network
from core.handler import MyHandler
from utils.node_picker import pick_working_connection  # yeni helper
from dotenv import load_dotenv

load_dotenv(".env")


# show INFO logs on console
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)


async def send_stream_auto(
    node, peer_id: str, data: bytes, chunk_size: int = 2048, delay: float = 0.005
):
    try:
        print(f"[test_stream] start_stream -> {peer_id}")
        await node.start_stream(peer_id)
    except Exception as e:
        print(f"[test_stream] start_stream failed: {e}")
        return

    total = len(data)
    sent = 0
    chunk_idx = 0

    for i in range(0, len(data), chunk_size):
        chunk = data[i : i + chunk_size]
        try:
            await node.send_stream_message(peer_id, chunk)
            sent += len(chunk)
            chunk_idx += 1
            if chunk_idx % 4 == 0:
                print(
                    f"[test_stream] sent {sent}/{total} bytes to {peer_id} (chunks {chunk_idx})"
                )
        except Exception as e:
            print(f"[test_stream] send_stream_message failed at seq {chunk_idx}: {e}")
            break
        await asyncio.sleep(delay)

    try:
        print(f"[test_stream] closing stream to {peer_id}")
        await node.close_stream(peer_id)
        print(f"[test_stream] close_stream done ({sent}/{total})")
    except Exception as e:
        print(f"[test_stream] close_stream failed: {e}")


async def watch_streams(node, interval=0.2):
    while True:
        active = await node.get_active_streams()
        if active:
            print("[watch] active streams:", active)
            for p in active:
                if await node.stream_ready(p):
                    data = await node.get_stream_batch(p)
                    print(f"[watch] got batch from {p[:12]} size={len(data)}")
        await asyncio.sleep(interval)


async def main():
    # 1. JWT
    token = create_jwt()
    print("🔑 Generated JWT token")

    # 2. Bootstrap + Network
    boot = Bootstrap(token)
    network = Network(boot)

    # 3. Handler bağla ve event loop başlat
    network.handler = MyHandler()
    await network.start()
    print("🔄 Event loop started")

    await asyncio.sleep(2)

    # 4. Discover
    nodes = await network.discover()
    print(f"🔍 Discovered {len(nodes.nodes)} peers")

    for n in nodes.nodes:
        print(f"   - {n.node_id[:20]} @ {len(n.connections)} connections available")

    # 5. Connect to discovered nodes (skip self)
    my_peer_id = boot.peer_id
    for n in nodes.nodes:
        if n.node_id == my_peer_id:
            continue

        working = await pick_working_connection(n.connections)
        if working is None:
            print(f"⚠ Cannot connect to {n.node_id[:12]}, skipping")
            continue

        ip, port = working
        try:
            print(f"↪ Connecting to {n.node_id[:12]} @ {ip}:{port}")
            await network.connect(n.node_id, ip, port)
            print(f"   ✓ Connect initiated to {n.node_id[:12]}")
        except Exception as e:
            print(f"   ✗ Failed to connect: {e}")

    # 6. Wait for peers
    for i in range(5):
        await asyncio.sleep(1)
        peers = await network.get_remote_peers()
        print(f"[{i+1}/5] Remote connected peers: {len(peers)}")
        if peers:
            break

    peers = await network.get_remote_peers()
    if not peers:
        print("⚠️ No remote peers connected")
    else:
        target = peers[0]
        print(f"🎯 Target peer: {target[:12]}")

        # 7. Send test message
        print("📤 Sending test message to target...")
        await network.send(target, b"Hello from class-based Network!")
        await asyncio.sleep(1)

    # 8. Broadcast / control loop
    print("\n🎧 Listening (type 'exit' to quit, 'test_stream' to start stream test)")
    stream_tasks = []
    node = await network.get_node()

    try:
        while True:
            cmd = await asyncio.to_thread(
                input, "💬 Command (broadcast/test_stream/exit): "
            )
            cmd = cmd.strip()

            if cmd.lower() == "exit":
                break

            if cmd.lower() == "test_stream":
                print(f"[main] starting test stream to {target[:12]}")
                big_data = b"STREAM-DATA-" * 4096 * 10

                async def run():
                    print("[DEBUG] start_stream")
                    await network.start_stream(target)

                    chunk_size = 16384
                    total_len = len(big_data)
                    start_time = asyncio.get_event_loop().time()

                    for i in range(0, total_len, chunk_size):
                        chunk = big_data[i : i + chunk_size]
                        await network.send_stream_message(target, chunk)
                        if (i // chunk_size) % 50 == 0:
                            await asyncio.sleep(0)

                    await network.close_stream(target)
                    end_time = asyncio.get_event_loop().time()
                    total_seconds = end_time - start_time
                    msg_count = total_len / 16
                    print(
                        f"Bitti! Süre: {total_seconds:.4f} sn. Frekans: {msg_count/total_seconds:.2f} msg/sec"
                    )

                asyncio.create_task(run())
                continue

            if cmd == "":
                continue

            await network.broadcast(cmd.encode())
            await asyncio.sleep(0.05)

    finally:
        if stream_tasks:
            print("[main] waiting for stream tasks to finish...")
            try:
                await asyncio.wait_for(asyncio.gather(*stream_tasks), timeout=30.0)
            except asyncio.TimeoutError:
                print(
                    "[main] stream tasks did not finish within timeout, cancelling..."
                )
                for t in stream_tasks:
                    t.cancel()

        await network.stop()
        print("👋 Network stopped")


if __name__ == "__main__":
    asyncio.run(main())
