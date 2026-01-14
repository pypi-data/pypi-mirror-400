import asyncio
from typing import Optional, Tuple
from streams_network import ConnectionInfo


async def try_connect(
    conn: ConnectionInfo, timeout: float = 0.5
) -> Optional[Tuple[str, int]]:
    ip = conn.address
    port = int(conn.port)
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(ip, port), timeout=timeout
        )
        writer.close()
        await writer.wait_closed()
        print(f"[helper] successful connection: {ip}:{port} ({conn.con_type})")
        return ip, port
    except Exception as e:
        # print(f"[helper] failed connection: {ip}:{port} ({conn.con_type}) -> {e}")
        return None


async def pick_working_connection(
    connections: list[ConnectionInfo], total_timeout: float = 2.0
) -> Optional[Tuple[str, int]]:
    tasks = [asyncio.create_task(try_connect(c, timeout=0.5)) for c in connections]

    done, pending = await asyncio.wait(
        tasks, return_when=asyncio.FIRST_COMPLETED, timeout=total_timeout
    )

    # İlk başarılı sonucu al
    for t in done:
        res = t.result()
        if res is not None:
            # geri kalan task'ları iptal et
            for p in pending:
                p.cancel()
            return res

    # hiçbir başarılı yoksa
    for p in pending:
        p.cancel()
    print("[helper] no working connection found within timeout")
    return None
