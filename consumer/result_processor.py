from dependency_graph.node import Node
from dependency_graph.executable_node import ExecutableNode
from dependency_graph.sentinel_node import SentinelNode
import asyncio

class ResultProcessor:
    def __init__(self, result_queue: asyncio.Queue[Node]):
        self._result_queue = result_queue
        self.running = False

    @property
    def task(self):
        return self._task

    async def process(self):
        try:
            while True:
                node = await self._result_queue.get()
                print(f"Processed {node.name}")
                if isinstance(node, ExecutableNode):
                    if node.result:
                        node.mark_as_executed()
                    self._result_queue.task_done()
                elif isinstance(node, SentinelNode):
                    self._result_queue.task_done()
                    break
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            print("ResultProcessor cancelled")

    def start(self):
        self.running = True
        self._task = asyncio.create_task(self.process())

    def stop(self):
        self._running = False
        self._task.cancel()