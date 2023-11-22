import time


def fib(n: int) -> int:
    if n <= 1:
        return n
    else:
        return (fib(n-1) + fib(n-2))

import asyncio


async def task_func1():
    await asyncio.sleep(1)
    print("Task 1")
    return True

async def task_func2():
    await asyncio.sleep(2)
    print("Task 2")
    return True

def task_func3():
    time.sleep(1)
    # fib(30)
    print("Task 3")
    return True

async def task_func4():
    await asyncio.sleep(3)    
    print("Task 4")
    return True

async def task_func5():
    await asyncio.sleep(2)    
    print("Task 5")
    return True

async def task_func6():
    await asyncio.sleep(3)    
    print("Task 6")
    return True

async def task_func7(): 
    await asyncio.sleep(15)   
    print("Task 7")
    return True