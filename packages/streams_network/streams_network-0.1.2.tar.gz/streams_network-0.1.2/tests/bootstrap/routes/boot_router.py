from fastapi import APIRouter, Depends, Response
from core import Bootstrap
import logging
from typing import List, Optional
from time import time
from models.nodes import Node, Nodes
from utils.constants import DEFAULT_P2P_TTL
from utils import verify_token
import asyncio

logger = logging.getLogger("Bootstrap")
router = APIRouter()
bootstrap = Bootstrap()


@router.post("/connect", response_model=Nodes)
async def connect_node(node: Node, payload: dict = Depends(verify_token)):
    await bootstrap.node_updates_queue.put(
        {"node": node, "owner": payload.get("owner")}
    )
    resp = Nodes(nodes=bootstrap.nodes[:8])
    print(resp)
    return resp


@router.post("/ping")
async def ping_node(node: Node, payload: dict = Depends(verify_token)):
    await bootstrap.node_updates_queue.put(
        {"node": node, "owner": payload.get("owner")}
    )
    return Response(status_code=202)
