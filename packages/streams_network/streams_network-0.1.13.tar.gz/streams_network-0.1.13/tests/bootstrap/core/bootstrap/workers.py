from fastapi import APIRouter, Depends, Response
from .bootstrap import Bootstrap
import logging
from typing import List, Optional
from time import time
from models.nodes import Node, Nodes
from utils.constants import DEFAULT_P2P_TTL
from utils import verify_token
import asyncio

logger = logging.getLogger("Bootstrap worker")


async def perform_bulk_update(updates: List[dict]):
    instance = Bootstrap()
    current_time = time()

    if not isinstance(instance.nodes, list):
        pass

    # Temizlik işlemi
    original_count = len(instance.nodes)
    instance.nodes = [n for n in instance.nodes if not n.ttl or n.ttl > current_time]

    expired_count = original_count - len(instance.nodes)
    if expired_count > 0:
        logger.info(f"Cleanup: Removed {expired_count} expired nodes")

    for item in updates:
        node_data: Node = item["node"]
        owner = item["owner"]

        found = False
        for n in instance.nodes:
            if n.node_id == node_data.node_id and n.owner == owner:
                n.ttl = current_time + DEFAULT_P2P_TTL
                found = True
                break

        if not found:
            node_data.ttl = current_time + DEFAULT_P2P_TTL
            node_data.owner = owner
            instance.nodes.append(node_data)

    logger.info(
        f"Batch processed {len(updates)} updates. Total nodes: {len(instance.nodes)}"
    )


async def batch_update_worker():
    logger.info("Batch Update worker is running")
    bootstrap = Bootstrap()
    while True:
        updates = []
        try:
            node_data = await bootstrap.node_updates_queue.get()
            updates.append(node_data)

            while len(updates) < 500:
                try:
                    next_node = bootstrap.node_updates_queue.get_nowait()
                    updates.append(next_node)
                except asyncio.QueueEmpty:
                    break
        except Exception as e:
            logger.error(f"Worker error: {e}")
            await asyncio.sleep(1)
            continue

        if updates:
            await perform_bulk_update(updates)
            for _ in range(len(updates)):
                bootstrap.node_updates_queue.task_done()
