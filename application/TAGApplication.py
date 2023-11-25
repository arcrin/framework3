from dependency_graph.executable_node import ExecutableNode
from dependency_graph.node import Node
from dependency_graph.sentinel_node import SentinelNode
from util.dag_vis import draw_graph
from sample_profile.scripts import *
from concurrent.futures import Future
from typing import Dict, Any, List, Callable, Coroutine, TypeVar
from util.timing_vis import plot_task_timing
import matplotlib.pyplot as plt
import datetime
import time
import functools
import asyncio

T = TypeVar('T')

class TAGApplication:
    def __init__(self):
        self.executable_task_queue: asyncio.Queue[Node] = asyncio.Queue()
        self.shared_result_space: Dict[str, Future[Any]] = {}
        self.sentinel_node = SentinelNode("EndOfTests")
        self.executalbe_nodes: List[ExecutableNode] = []
        self.task_timing: List[Dict[str, Any]] = []
    
    def load_nodes(self, nodes: List[ExecutableNode]):
        self.executalbe_nodes = nodes

    async def enqueue_executable_tasks(self):
        while any(not node.executed for node in self.executalbe_nodes):
            for node in self.executalbe_nodes:
                if node.ready_to_execute():
                    await self.executable_task_queue.put(node)
                    print(f'{node.name} queued')
                    node.mark_as_executing()
            await asyncio.sleep(0.1)
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


    async def run(self):
        enqueue_task = asyncio.create_task(self.enqueue_executable_tasks()) 
        dequeue_task = asyncio.create_task(self.dequeue_and_execute_executable())
        await asyncio.gather(enqueue_task, dequeue_task)
        print("Application stoped")


    async def execute_task(self, node: ExecutableNode):
        node_result = await node.execute(self.shared_result_space)
        self.shared_result_space[node.name].set_result(node_result)

    

    def async_timed(self, node_name: str):
        def wrapper(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T]]:
            @functools.wraps(func)
            async def wrapped(*args: Any, **kwargs: Any) -> Any:
                start = time.time()
                try:
                    return await func(*args, **kwargs)
                finally:
                    end = time.time()
                    total = end -start
                    print(f'finished {func} in {total:.4f} seconds\n')
                    self.task_timing.append({"task": node_name,
                                    "start_time": start,
                                    "end_time": end})
            return wrapped
        return wrapper
    
    def plot_task_timing(self):
        fig, ax = plt.subplots()

        for i, task in enumerate(self.task_timing):
            start_time_seconds = task["start_time"] - self.task_timing[0]["start_time"]
            end_time_seconds = task["end_time"] - self.task_timing[0]["start_time"]
            execution_time_seconds = end_time_seconds - start_time_seconds
            ax.barh(i, execution_time_seconds, left=start_time_seconds)

        ax.set_yticks(range(len(self.task_timing)))
        ax.set_yticklabels([task["task"] for task in self.task_timing])
        ax.set_xlabel("Seconds")
        ax.set_title("Function Execution Timeline")

        plt.savefig('function_execution_timeline.pdf')