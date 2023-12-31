from typing import List
from dependency_graph.node import Node
from dependency_graph.executable_node import ExecutableNode
from dependency_graph.sentinel_node import SentinelNode
import asyncio

class ExecutableNodeEnqueuer:
    def __init__(self, 
                 executable_task_queue: asyncio.Queue[Node], 
                 nodes: List[ExecutableNode]):
        self._queue = executable_task_queue
        self._nodes = nodes
        self._running = False

    @property
    def task(self):
        return self._task

    async def enqueue(self):
        try:
            while any(not node.executed for node in self._nodes):
                for node in self._nodes:
                    if node.ready_to_execute():
                        await self._queue.put(node)
                        print(f"Enqueued {node.name}")
                        node.mark_as_executing()
                await asyncio.sleep(0.1)
            self._queue.put_nowait(SentinelNode("EndOfTests"))
            print("Enqueue stopped")
        except asyncio.CancelledError:
            print("Enqueue cancelled")
    
    def start(self):
        self._running = True
        self._task = asyncio.create_task(self.enqueue())

    def stop(self):
        self._running = False 
        self._task.cancel()