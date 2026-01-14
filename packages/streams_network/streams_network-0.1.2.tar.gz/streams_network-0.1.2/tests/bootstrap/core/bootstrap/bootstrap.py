from models.nodes import Node, Nodes
import asyncio


class Bootstrap:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Bootstrap, cls).__new__(cls)
            cls._instance._init_status = False
        return cls._instance

    def __init__(self):
        if self._init_status:
            return
        self._init_status = True
        self.node_updates_queue = asyncio.Queue()
        self.nodes: Nodes = []

    async def get_network_nodes(self, node: Node):
        _id = node.node_id
        owner = node.owner
