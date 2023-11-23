from application.dependency_graph import Node
from util.dag_vis import draw_graph
from sample_profile.scripts import *
from concurrent.futures import Future
from typing import Dict, Any
from util.timing_vis import plot_task_timing
import asyncio


# Create some nodes
node1 = Node("task1", task_func1)
node2 = Node("task2", task_func2)
node3 = Node("task3", task_func3)
node4 = Node("task4", task_func4)
node5 = Node("task5", task_func5)
node6 = Node("task6", task_func6)
node7 = Node("task7", task_func7)

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

async def execute_task(node: Node, results: Dict[str, Future[Any]]):
    result = await node.execute(results)
    results[node.name].set_result(result)
async def main():
    # Create a dictionary to store the Future of each task
    results: Dict[str, Future[Any]] = {node.name: Future() for node in nodes}
    # Create a queue for tasks that are ready to execute
    ready_to_execute_queue: asyncio.Queue[Node] = asyncio.Queue()

    # Start checking for node readiness and queing tasks
    async def check_and_enqueue():
        # while any(not node.cleared for node in nodes):
        #     for node in nodes: 
        #         if node.ready_to_execute():
        #             await ready_to_execute_queue.put(node)
        #             node.mark_as_executing()
        #     await asyncio.sleep(0.1)
        # print("check_and_enqueue complete")
        # return True
        for i in range(10):
            print(f'task1 iteration {i}')
            await asyncio.sleep(1)
        print('check_and_enqueue done')

    # Start executing tasks from the queue
    async def execute_from_queue():
        # while True:
        #     if ready_to_execute_queue.empty() and all(node.cleared for node in nodes):
        #         break
        #     node = await ready_to_execute_queue.get()
        #     asyncio.create_task(execute_task(node, results))
        #     ready_to_execute_queue.task_done()
        #     await asyncio.sleep(0.1)
        # print("execute_from_queue complete")
        # return True
        for i in range(10):
            print(f'task2 iteration {i}')
            await asyncio.sleep(1.5)
        print('execute_from_queue done')

    check_and_enqueue_task = asyncio.create_task(check_and_enqueue())
    execution_task = asyncio.create_task(execute_from_queue())

    # done, pending = await asyncio.wait([check_and_enqueue_task, execution_task], return_when=asyncio.FIRST_COMPLETED)

    # for task in pending:
    #     task.cancel()

    asyncio.gather(check_and_enqueue_task, execution_task)
    print("Gather complete")
    # plot_task_timing()

if __name__ == "__main__":
    asyncio.run(main())