from application.TAGApplication import TAGApplication
from dependency_graph.executable_node import ExecutableNode
from sample_profile.scripts import *

# Create some nodes
node1 = ExecutableNode("task1", task_func1)
node2 = ExecutableNode("task2", task_func2)
node3 = ExecutableNode("task3", task_func3)
node4 = ExecutableNode("task4", task_func4)
node5 = ExecutableNode("task5", task_func5)
node6 = ExecutableNode("task6", task_func6)
node7 = ExecutableNode("task7", task_func7)

# Add dependencies
node1.add_dependency(node2)
node2.add_dependency(node3)
node1.add_dependency(node4)
node4.add_dependency(node5)
node3.add_dependency(node5)
node2.add_dependency(node6)
node6.add_dependency(node7)

nodes = [node1, node2, node3, node4, node5, node6, node7]

app = TAGApplication()
app.load_nodes(nodes)
app.load_components()
asyncio.run(app.run())
app.analysis()