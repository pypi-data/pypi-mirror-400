from typing import List, Optional
from pydantic import BaseModel


class ConnectionInfo(BaseModel):
    con_type: str  # LAN, VPN, Public
    address: str  # IP
    port: str  # Port


class Node(BaseModel):
    node_id: str
    owner: str
    valid: Optional[bool] = True
    ttl: Optional[float] = None
    connections: List[ConnectionInfo] = []


class Nodes(BaseModel):
    nodes: List[Node] = []
