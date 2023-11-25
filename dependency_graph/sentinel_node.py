from dependency_graph.node import Node

class SentinelNode(Node):
    def __init__(self, name: str):
        super().__init__(name)

    @property
    def executed(self) -> bool:
        return True
