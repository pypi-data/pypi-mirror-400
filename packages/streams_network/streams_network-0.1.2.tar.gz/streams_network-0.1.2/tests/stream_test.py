import asyncio
import random
import struct
from streams_network import BootstrapNetwork, P2PNode
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


# --- Gelişmiş Handler ---
class StreamHandler:
    def on_message(self, peer_id: str, payload: bytes) -> bytes:
        return b"ACK"

    def on_peer_connected(self, peer_id: str) -> None:
        print(f"🤝 Connected to: {peer_id[:15]}...")

    def on_stream_message(self, peer_id: str, message: bytes):
        # Endüstriyel veri paketini çözme (örnek: f32 sıcaklık verisi)
        try:
            val = struct.unpack("f", message)[0]
            print(f"📈 [STREAM] {peer_id[:8]} -> Sensor Value: {val:.2f}")
        except:
            print(f"📥 [STREAM] {peer_id[:8]} -> Raw: {message.hex()}")

    def on_stream_response(self, peer_id: str, message: bytes):
        print(f"📤 [STREAM RESP] From {peer_id[:8]}")


async def run_stream_test():
    # 1. Başlangıç Ayarları (Önceki örnekteki gibi JWT ve Config)
    # Not: Hızlı test için statik değerler kullanıyoruz

    token = create_jwt(
        owner="user1", email="user1@example.com", expires_in_seconds=3600
    )
    print(f"🔑 Generated JWT token")

    config = BootstrapNetwork(
        bearer_token=token,
        ip="127.0.0.1",
        owner="user1",
        port=0,
        bootstrap_url="http://127.0.0.1:8000",
    )

    node = await P2PNode.create(config)
    handler = StreamHandler()
    await node.start_event_loop(handler)

    print(f"🚀 Node Started: {node.peer_id()}")

    # 2. Peer Keşfi ve Bağlantı
    print("🔍 Searching for peers...")
    discovery = await node.peer_discover()
    target_peer = None

    for p in discovery.nodes:
        if p.node_id != node.peer_id():
            try:
                print(f"➡️ Connecting to peer: {p.node_id[:15]} at {p.ip}:{p.port}")
                await node.connect(p.node_id, p.ip, p.port)
                target_peer = p.node_id
            except Exception as e:
                print(f"❌ Connection failed to {p.node_id[:15]}: {e}")

    if not target_peer:
        print("⚠️ No target peer found for streaming. Start another instance!")
        return

    await asyncio.sleep(2)  # Bağlantının oturması için bekle

    # 3. STREAM SİMÜLASYONU (Plotune Data Flow)
    print(f"\n🌊 Starting Stream Test to {target_peer[:15]}...")

    # Alıcı tarafta (kendi tarafımızda da olabilir) buffer'ı başlatıyoruz
    await node.start_stream(target_peer)

    try:
        for i in range(20):  # 20 paket gönderelim
            # Örnek endüstriyel veri: 20.0 ile 30.0 arası rastgele sıcaklık
            sensor_data = random.uniform(20.0, 30.0)
            payload = struct.pack("f", sensor_data)  # f32 formatında paketle

            # Rust tarafındaki send_stream_message çağrısı (prefix 1u8 ekler)
            await node.send_stream_message(target_peer, payload)

            await asyncio.sleep(0.2)  # 200ms aralıkla gönder (5Hz)

            if i % 5 == 0:
                active = await node.get_active_streams()
                print(f"ℹ️ Active streams: {active}")

        # 4. Stream Kapatma ve Biriken Veriyi Alma
        print("\n🏁 Closing stream and retrieving accumulated data...")
        accumulated_raw = await node.close_stream(target_peer)

        # Biriken veriyi analiz et (Her paket 4 byte f32)
        total_readings = len(accumulated_raw) // 4
        print(f"📊 Total data chunks accumulated in Rust buffer: {total_readings}")

    except Exception as e:
        print(f"❌ Stream Error: {e}")
    finally:
        await node.stop_event_loop()


if __name__ == "__main__":
    asyncio.run(run_stream_test())
