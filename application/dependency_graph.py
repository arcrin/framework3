from typing import Any, Set, List, Dict, Coroutine


class Node:
    def __init__(self, name: str, task: Coroutine[Any, Any, Any]):
        self.name = name
        self.task = task
        self.children: List[Node] = []
        self.dependencies: Set[Node] = set()

    def ready(self):
        return len(self.dependencies) == 0

    def clear(self):
        for child in self.children:
            child.dependencies.remove(self)



class DAG:
    def __init__(self):
        self.nodes: Dict[str, Node] = {}

    def add_node(self, name: str, task: Coroutine[Any, Any, Any]):
        if name not in self.nodes:
            self.nodes[name] = Node(name, task)
        return self.nodes[name]

    def add_edge(self, parent_name: str, child_name: str, parent_task: Coroutine[Any, Any, Any], child_task: Coroutine[Any, Any, Any]):
        parent_node = self.add_node(parent_name, parent_task)
        child_node = self.add_node(child_name, child_task)
        parent_node.children.append(child_node)
        child_node.dependencies.add(parent_node)

    async def execute(self):
        queue = [node for node in self.nodes.values() if node.ready()]
        while queue:
            node = queue.pop(0)
            await node.task
            node.clear()
            queue.extend(child for child in node.children if child.ready())