from application.dependency_graph import Node
from util.dag_vis import draw_graph
from util.async_timing import async_timed
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from time import sleep
from sample_profile.scripts import *
import asyncio


# Create some nodes
node1 = Node("1", task_func1)
node2 = Node("2", task_func2)
node3 = Node("3", task_func3)
node4 = Node("4", task_func4)
node5 = Node("5", task_func5)
node6 = Node("6", task_func6)
node7 = Node("7", task_func7)

# Add dependencies
node1.add_dependency(node2)
node2.add_dependency(node3)
node1.add_dependency(node4)
node4.add_dependency(node5)
node3.add_dependency(node5)
node2.add_dependency(node6)
node6.add_dependency(node7)

nodes = [node1, node2, node3, node4, node5, node6, node7]

# Draw the graph
# draw_graph(node1)

async def execute_task(node: Node):
    if asyncio.iscoroutinefunction(node.task):
        await node.task()
        node.clear()
    else:
        with ProcessPoolExecutor() as executor:
            await asyncio.get_running_loop().run_in_executor(executor, node.task)
            node.clear()

async def main():
    # Create a queue for tasks that are ready to execute
    ready_to_execute_queue: asyncio.Queue[Node] = asyncio.Queue()

    # Start checking for node readiness and queing tasks
    async def check_and_enqueue():
        while any(not node.cleared for node in nodes):
            for node in nodes: 
                if node.ready_to_execute():
                    await ready_to_execute_queue.put(node)
                    nodes.remove(node)
            await asyncio.sleep(0.1)

    # Start executing tasks from the queue
    async def execute_from_queue():
        while True:
            node = await ready_to_execute_queue.get()
            asyncio.create_task(execute_task(node))
            ready_to_execute_queue.task_done()
            await asyncio.sleep(1)

    check_and_enqueue_task = asyncio.create_task(check_and_enqueue())
    execution_task = asyncio.create_task(execute_from_queue())

    await asyncio.gather(check_and_enqueue_task, execution_task)

if __name__ == "__main__":
    asyncio.run(main())