from dependency_graph.executable_node import ExecutableNode
from dependency_graph.sentinel_node import SentinelNode
from util.timing_vis import plot_task_timing
from dependency_graph.node import Node
from util.dag_vis import draw_graph
from sample_profile.scripts import *
from typing import Dict, Any, List
import asyncio

class NodeList:
    def __init__(self, nodes_state: asyncio.Event):
        self._nodes: List[Node] = []
        self._nodes_state = nodes_state

    def add_node(self, node: Node):
        self._nodes.append(node)
        self._nodes_state.set()

    def remove_node(self, node: Node):
        pass

        

# TODO: now I need to handle failures and errors from nodes
class TAGApplication:
    def __init__(self):
        self.executable_task_queue: asyncio.Queue[Node] = asyncio.Queue()
        self.result_process_queue: asyncio.Queue[Node] = asyncio.Queue()
        self.sentinel_node = SentinelNode("EndOfTests")
        self.executalbe_nodes: List[ExecutableNode] = []
        self.task_timing: List[Dict[str, Any]] = []
        self._primary_node: ExecutableNode
        self._dag_state_change = asyncio.Event()
        self._dag_state_change.set()
        self.client = None

    # TODO: need a proper load function based on the profile
    # load profile also need to initialize the shared_result_space
    def load_nodes(self, nodes: List[ExecutableNode]):
        self.executalbe_nodes = nodes
        self._primary_node = nodes[0]

    async def enqueue_executables(self):
        try:
            while any([not node.executed for node in self.executalbe_nodes]):
                await self._dag_state_change.wait()
                for node in self.executalbe_nodes:
                    if node.ready_to_execute():
                        await self.executable_task_queue.put(node)
                        print(f"Enqueued {node.name}")
                        node.mark_as_executing()
                self._dag_state_change.clear()
            self.executable_task_queue.put_nowait(self.sentinel_node)
            print("Enqueued stopped")
        except asyncio.CancelledError:
            print("Enqueue cancelled")

    async def execute_node(self, node: ExecutableNode):
        await node.execute()
        await self.result_process_queue.put(node)

    async def dequeue_executables(self):
        try:
            while True:
                node = await self.executable_task_queue.get()
                print(f"Dequeued {node.name}")
                if isinstance(node, ExecutableNode):
                    asyncio.create_task(self.execute_node(node))
                    self.executable_task_queue.task_done()
                elif isinstance(node, SentinelNode):
                    self.executable_task_queue.task_done()
                    await self.result_process_queue.put(SentinelNode("EndOfTests"))
                    break
        except asyncio.CancelledError:
            print("Dequeue cancelled")

    async def process_result(self):
        try:
            while True:
                node = await self.result_process_queue.get()
                if isinstance(node, ExecutableNode):
                    if node.result:
                        node.mark_as_executed()
                    elif node.exception:
                        print(f"{node.name} failed with exception {node.exception}")
                        asyncio.create_task(self.handle_user_input(node))
                    self.result_process_queue.task_done()
                elif isinstance(node, SentinelNode):
                    self.result_process_queue.task_done()
                    break
                print(f"{node.name} result processed")
                self._dag_state_change.set()
        except asyncio.CancelledError:
            print("Result processing cancelled")

    async def handle_user_input(self, node: ExecutableNode):
        response = await asyncio.get_event_loop().run_in_executor(None, input, "Do you want to retry? (y/n)")
        if response == "y":
            node.mark_as_to_execute()
        else:
            node.mark_as_executed()

    async def run(self):
        enqueue_task = asyncio.create_task(self.enqueue_executables())
        dequeue_task = asyncio.create_task(self.dequeue_executables())
        result_process_task = asyncio.create_task(self.process_result())
        await asyncio.gather(enqueue_task,
                             dequeue_task,
                             result_process_task,
                             )
        print("Application finished")

    def analysis(self):
        draw_graph(self.executalbe_nodes[0])
        plot_task_timing()