from dependency_graph.executable_node import ExecutableNode
from dependency_graph.node import Node
from dependency_graph.sentinel_node import SentinelNode
from util.dag_vis import draw_graph
from sample_profile.scripts import *
from concurrent.futures import Future
from typing import Dict, Any, List
from util.timing_vis import plot_task_timing
from producer.executable_node_enqueuer import ExecutableNodeEnqueuer
from consumer.executable_node_dequeuer import ExecutableNodeDequeuer
import asyncio


# TODO: now I need to handle failures and errors from nodes
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

    def load_components(self):
        self._executable_node_enqueuer = ExecutableNodeEnqueuer(self.executable_task_queue, self.executalbe_nodes)
        self._executable_node_dequeuer = ExecutableNodeDequeuer(self.executable_task_queue, self.shared_result_space)

    async def run(self):
        self._executable_node_enqueuer.start()
        self._executable_node_dequeuer.start()
        await asyncio.gather(self._executable_node_enqueuer.task, 
                             self._executable_node_dequeuer.task)
        print("Application stoped")

    def analysis(self):
        draw_graph(self.executalbe_nodes[0])
        plot_task_timing()