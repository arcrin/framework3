from graphviz import Digraph
from application.dependency_graph import Node
from typing import Set


def draw_graph(root: Node):
    dot = Digraph()
    visited: Set['Node'] = set()

    def add_edges(node: Node):
        if node not in visited:
            dot.node(node.name)
            for dependency in node.dependencies:
                dot.edge(node.name, dependency.name)
                add_edges(dependency)
            visited.add(node)
    add_edges(root)
    dot.render('dag.gv', view=True)


    