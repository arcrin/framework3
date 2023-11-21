from application.dependency_graph import DAG
from util.dag_vis import draw_graph
import asyncio


async def task1():
    await asyncio.sleep(1)
    print('task1')

async def task2():
    await asyncio.sleep(2)
    print('task2')

async def task3():  
    await asyncio.sleep(3)
    print('task3')

async def task4():
    await asyncio.sleep(4)
    print('task4')

async def task5():
    await asyncio.sleep(5)
    print('task5')

async def task6():
    await asyncio.sleep(6)
    print('task6')

async def task7():
    await asyncio.sleep(7)
    print('task7')



dag = DAG()
dag.add_edge('Node1', 'Node2', task1(), task2())
dag.add_edge('Node1', 'Node3', task1(), task3())
dag.add_edge('Node2', 'Node4', task2(), task4())
dag.add_edge('Node2', 'Node5', task2(), task5())
dag.add_edge('Node3', 'Node6', task3(), task6())
dag.add_edge('Node4', 'Node7', task4(), task7())
dag.add_edge('Node5', 'Node7', task5(), task7())
dag.add_edge('Node6', 'Node7', task6(), task7())

draw_graph(dag)


asyncio.run(dag.execute())