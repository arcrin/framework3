from typing import Dict, Any
from concurrent.futures import Future
from dependency_graph.executable_node import ExecutableNode
from dependency_graph.node import Node  
import asyncio

class ExecutableNodeDequeuer:
    def __init__(self, queue: asyncio.Queue[Node], result_space: Dict[str, Future[Any]]):
        self._queue = queue
        self.running = False
        self._result_space = result_space

    @property
    def task(self):
        return self._task

    async def _execute_node(self, node: ExecutableNode):
        node_result = await node.execute(self._result_space)
        self._result_space[node.name].set_result(node_result)

    async def dequeue(self):
        try:
            while True:
                node = await self._queue.get()
                print(f"Dequeued {node.name}")
                if isinstance(node, ExecutableNode):
                    asyncio.create_task(self._execute_node(node))
                self._queue.task_done()
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            print("Dequeue cancelled")

    def start(self):
        self.running = True
        self._task = asyncio.create_task(self.dequeue())

    def stop(self):
        self.running = False
        self._task.cancel()
