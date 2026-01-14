from typing import Optional, List, Any

class ConnectionInfo:
    con_type: str
    address: str
    port: str

    def __init__(self, con_type: str, address: str, port: str) -> None: ...

class Node:
    node_id: str
    owner: str
    connections: List[ConnectionInfo]

    def __init__(
        self, node_id: str, owner: str, connections: List[ConnectionInfo]
    ) -> None: ...

class Nodes:
    nodes: List[Node]

    def __init__(self, nodes: List[Node]) -> None: ...

class BootstrapNetwork:
    bootstrap_url: str
    bearer_token: str
    owner: str
    connections: List[ConnectionInfo]

    def __init__(
        self,
        bearer_token: str,
        connections: Optional[List[ConnectionInfo]] = None,
        bootstrap_url: Optional[str] = None,
        owner: Optional[str] = None,
    ) -> None: ...
    def add_connection(self, type_: str, address: str, port: str) -> None: ...
    def get_peer_id(self) -> str: ...

class P2PNode:
    # Creation
    @staticmethod
    async def create(config: BootstrapNetwork) -> "P2PNode": ...

    # Identity
    def peer_id(self) -> str: ...
    def listen_port(self) -> int: ...

    # Peer Management
    async def peer_discover(self) -> Nodes: ...
    async def connect(self, peer_id: str, ip: str, port: str) -> None: ...
    async def disconnect(self, peer_id: str) -> None: ...
    async def get_peers(self) -> List[str]: ...

    # Messaging (Request / Response)
    async def send_message(self, peer_id: str, msg: bytes) -> bytes: ...
    async def broadcast(
        self,
        msg: bytes,
        exclude: Optional[List[str]] = None,
    ) -> None: ...

    # Stream Messaging (Raw / Chunked)
    async def start_stream(self, peer_id: str) -> None: ...
    async def send_stream_message(self, peer_id: str, msg: bytes) -> None: ...
    async def stream_ready(self, peer_id: str) -> bool: ...
    async def get_stream_batch(self, peer_id: str) -> bytes: ...
    async def close_stream(self, peer_id: str) -> bytes: ...
    async def get_active_streams(self) -> List[str]: ...

    # Event Loop
    async def start_event_loop(self, handler: Optional[Any] = None) -> None:
        """
        Starts the background swarm + event processing loop.
        Non-blocking. Safe to call once.
        """
        ...

    async def stop_event_loop(self) -> None:
        """Stops the background event loop."""
        ...
    # Utility
    async def ping(self, peer_id: str) -> bool: ...

class MessageHandler:
    """
    Optional handler interface.
    Implement any subset of these methods.
    """

    def on_message(self, peer_id: str, payload: bytes) -> bytes:
        """
        Called on incoming request.
        Return bytes to send as response.
        """
        ...

    def on_response(self, peer_id: str, payload: bytes) -> None:
        """Called when a response is received."""
        ...

    def on_peer_connected(self, peer_id: str) -> None:
        """Called when a peer connects."""
        ...

    def on_peer_disconnected(self, peer_id: str) -> None:
        """Called when a peer disconnects."""
        ...

    def on_stream_message(self, peer_id: str, message: bytes) -> None:
        """
        Called when a raw stream chunk is received.
        Accumulation is handled internally by Rust.
        """
        ...

    def on_stream_response(self, peer_id: str, message: bytes) -> None:
        """Called when a stream response is received."""
        ...
