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
import websockets


# TODO: now I need to handle failures and errors from nodes
class TAGApplication:
    def __init__(self):
        self.executable_task_queue: asyncio.Queue[Node] = asyncio.Queue()
        self.result_process_queue: asyncio.Queue[Node] = asyncio.Queue()
        self.shared_result_space: Dict[str, Future[Any]] = {}
        self.sentinel_node = SentinelNode("EndOfTests")
        self.executalbe_nodes: List[ExecutableNode] = []
        self.task_timing: List[Dict[str, Any]] = []
        self._primary_node: ExecutableNode
        self.client = None
    
    async def websocket_conn_handler(self, client_websocket, path):
        self.client = client_websocket
        try:
            async for message in self.client:
                print(f'Client message: {message}')
        except websockets.exceptions.ConnectionClosed:
            print('Connection closed')

    # TODO: need a proper load function based on the profile
    # load profile also need to initialize the shared_result_space
    def load_nodes(self, nodes: List[ExecutableNode]):
        self.executalbe_nodes = nodes
        self._primary_node = nodes[0]
        self.shared_result_space = {node.name: Future() for node in nodes}

    def load_components(self):
        self._executable_node_enqueuer = ExecutableNodeEnqueuer(self.executable_task_queue, self.executalbe_nodes)
        self._executable_node_dequeuer = ExecutableNodeDequeuer(self.executable_task_queue, self.result_process_queue)

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
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            print("Result processing cancelled")

    async def handle_user_input(self, node: ExecutableNode):
        response = await asyncio.get_event_loop().run_in_executor(None, input, "Do you want to retry? (y/n)")
        if response == "y":
            node.mark_as_to_execute()
        else:
            node.mark_as_executed()

    async def handle_websocket_user_input(self, node: ExecutableNode):
        await self.websocket.send(f"{node.name} failed with exception {node.exception}. Do you want to retry? (y/n)")
        response = await self.websocket.recv()
        if response == "y":
            node.mark_as_to_execute()
        else:
            node.mark_as_executed()

    async def run(self):
        start_websocket_server = websockets.serve(self.websocket_conn_handler, 'localhost', 8765)
        self._executable_node_enqueuer.start()
        self._executable_node_dequeuer.start()
        result_process_task = asyncio.create_task(self.process_result())
        await asyncio.gather(self._executable_node_enqueuer.task, 
                             self._executable_node_dequeuer.task,
                             result_process_task,
                             start_websocket_server
                             )
        print("Application finished")

    def analysis(self):
        draw_graph(self.executalbe_nodes[0])
        plot_task_timing()