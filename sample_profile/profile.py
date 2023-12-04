from typing import Callable
from dependency_graph.executable_node import ExecutableNode
from scripts import *
import asyncio


class SampleProfile:
    def __init__(self,
                 product_info_node: ExecutableNode,
                 test_jig_info_node: ExecutableNode) -> None:
        pass

        tc1 = ExecutableNode("task1", task_func1)
        tc2 = ExecutableNode("task2", task_func2)
        tc3 = ExecutableNode("task3", task_func3)
        tc4 = ExecutableNode("task4", task_func4)
        tc5 = ExecutableNode("task5", task_func5)
        tc6 = ExecutableNode("task6", task_func6)
        tc7 = ExecutableNode("task7", task_func7)

    def add_test(self):
        # TODO: I want this to become a producer. When the dependencies are ready, this function should produce
        # a test case node and push it to the queue OR I could use a async generator/iterator to send the test case 
        # node to a higher level. Here are some responsibilities of this function:
        # 1. Wrap the test function in a Node
        # 2. Check dependencies
        # 3. In order to check dependencies, the dependencies should be established before this point.
        pass