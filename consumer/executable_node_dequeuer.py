from dependency_graph.executable_node import ExecutableNode
from dependency_graph.sentinel_node import SentinelNode
from dependency_graph.node import Node  
import asyncio

class ExecutableNodeDequeuer:
    def __init__(self, 
                 task_queue: asyncio.Queue[Node],
                 result_queue: asyncio.Queue[Node]):
        self._queue = task_queue
        self.running = False
        self._result_queue = result_queue

    @property
    def task(self):
        return self._task

    async def _execute_node(self, node: ExecutableNode):
        await node.execute()
        await self._result_queue.put(node)


    async def dequeue(self):
        try:
            while True:
                node = await self._queue.get()
                print(f"Dequeued {node.name}")
                if isinstance(node, ExecutableNode):
                    asyncio.create_task(self._execute_node(node))
                    self._queue.task_done()
                elif isinstance(node, SentinelNode):
                    self._queue.task_done()
                    await self._result_queue.put(SentinelNode("EndOfTests"))
                    break
                # await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            print("Dequeue cancelled")

    def start(self):
        self.running = True
        self._task = asyncio.create_task(self.dequeue())

    def stop(self):
        self.running = False
        self._task.cancel()
