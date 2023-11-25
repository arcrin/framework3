from dependency_graph.executable_node import ExecutableNode
from dependency_graph.node import Node
from dependency_graph.sentinel_node import SentinelNode
from util.dag_vis import draw_graph
from sample_profile.scripts import *
from concurrent.futures import Future
from typing import Dict, Any, List
from util.timing_vis import plot_task_timing
import asyncio


class TAGApplication:
    def __init__(self):
        self.executable_task_queue: asyncio.Queue[Node] = asyncio.Queue()
        self.shared_result_space: Dict[str, Future[Any]] = {}
        self.sentinel_node = SentinelNode("EndOfTests")
        self.executalbe_nodes: List[ExecutableNode] = []
        self.task_timing: List[Dict[str, Any]] = []
        self._primary_node: ExecutableNode
    
    # TODO: need a proper load function based on the profile
    # load profile also need to initialize the shared_result_space
    def load_nodes(self, nodes: List[ExecutableNode]):
        self.executalbe_nodes = nodes
        self._primary_node = nodes[0]
        self.shared_result_space = {node.name: Future() for node in nodes}

    async def enqueue_executable_tasks(self):
        while any(not node.executed for node in self.executalbe_nodes):
            for node in self.executalbe_nodes:
                if node.ready_to_execute():
                    await self.executable_task_queue.put(node)
                    print(f'{node.name} queued')
                    node.mark_as_executing()
            await asyncio.sleep(0.1)
        await self.executable_task_queue.put(self.sentinel_node)
        print("enqueue_executable_tasks complete")

    async def dequeue_and_execute_executable(self):
        while True:
            node = await self.executable_task_queue.get()
            if isinstance(node, ExecutableNode):
                asyncio.create_task(self.execute_task(node))
            elif isinstance(node, SentinelNode):
                break
            self.executable_task_queue.task_done()
            await asyncio.sleep(0.1)
        print("dequeue_and_execute_executable complete")


    async def execute_task(self, node: ExecutableNode):
        node_result = await node.execute(self.shared_result_space)
        self.shared_result_space[node.name].set_result(node_result)

    async def run(self):
        enqueue_task = asyncio.create_task(self.enqueue_executable_tasks()) 
        dequeue_task = asyncio.create_task(self.dequeue_and_execute_executable())
        await asyncio.gather(enqueue_task, dequeue_task)
        print("Application stoped")

    def analysis(self):
        draw_graph(self.executalbe_nodes[0])
        plot_task_timing()