from graphviz import Digraph
from application.dependency_graph import DAG


def draw_graph(dag: DAG):
    dot = Digraph()

    for node in dag.nodes.values():
        dot.node(node.name)

    for node in dag.nodes.values():
        for child in node.children:
            dot.edge(node.name, child.name)

    dot.render('dag.gv', view=True)