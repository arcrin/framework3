from dependency_graph.executable_node import ExecutableNode
from dependency_graph.sentinel_node import SentinelNode
from util.timing_vis import plot_task_timing
from dependency_graph.node import Node
from util.dag_vis import draw_graph
from typing import Dict, Any, List
import asyncio

# TODO: I am having trouble with how to organize tasks. I have the Node class that allows me to make a dependency tree,
#  but I still need to manually create the dependencies between tasks. It is fine when it comes to test cases, because
#  they are defined in a profile class, and the dependencies are defined by whoever writes the test scripts. The process
#  related tasks are different. They are isolated from the test profile. If a test case is dependent on a process task,
#  it needs to know what kind of process it is waiting for; or the profile needs to know about it. How do I pass on this
#  information?
#  Create process task classes, make these classes awaitable. During profile creation, explicitly define the
#  dependencies between test cases and process tasks.

# TODO: How are process task objects created? "Load product info" process is initiated by user SN scan.
#  "load test jig configuration" is initiated inside the profile. I should identify all jobs first.
#  1. User input: scan SN; pass/fail prompt; other input
#  2. Get product info from database
#  3. Load profile: this is tricky. This is could also be the place where test cases are loaded, put on the queue
#  4. Load test jig configuration. This also happens inside the profile. This is where things get complicated
#  5. Push final result to mongo. Combine results from all test cases tasks and push them to mongo

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

    def load_profile(self,):
        # TODO: how to start a load profile procedure?
        # 1. download and install profile modeule like we are doing right now. (pip install sample_profile)
        # 2. import the module
        # 3. create an instance of this profile module
        # 4. I wouldn't be able to start adding test cases to the queue
        pass

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