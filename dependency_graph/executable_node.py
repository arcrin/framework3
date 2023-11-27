from dependency_graph.node import Node
from enum import Enum
from typing import Callable, Any
from util.async_timing import async_timed
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import asyncio


class ExecutionStatus(Enum):
    TO_EXECUTE = 1
    EXECUTING = 2
    EXECUTED = 4
    ERROR = 5

class ExecutableNode(Node):
    def __init__(self, name: str, task: Callable[..., Any]):
        super().__init__(name)
        self._task = task
        self._execution_status: ExecutionStatus = ExecutionStatus.TO_EXECUTE
        self._result = None
        self._exception = None
        self.execute = async_timed(self.name)(self.execute)
        
    def __str__(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return self._name 
    
    @property
    def result(self):
        return self._result
    
    @property
    def exception(self):
        return self._exception
    
    @property
    def executed(self) -> bool:
        return self._execution_status == ExecutionStatus.EXECUTED

    def mark_as_executed(self):
        self._execution_status = ExecutionStatus.EXECUTED

    def mark_as_executing(self):
        self._execution_status = ExecutionStatus.EXECUTING

    def mark_as_to_execute(self):
        self._execution_status = ExecutionStatus.TO_EXECUTE

    def ready_to_execute(self) -> bool:
        return all(dependency.executed for dependency in self.dependencies) and self._execution_status == ExecutionStatus.TO_EXECUTE
    
    async def execute(self):
        try:
            dependency_results = {dependency.name: dependency.result for dependency in self.dependencies}
            if asyncio.iscoroutinefunction(self._task):
                self._result = await self._task(**dependency_results)
            else:
                #TODO: ThreadPoolExecutor vs ProcessPoolExecutor
                with ThreadPoolExecutor() as executor:
                    partial_func = partial(self._task, **dependency_results)
                    self._result = await asyncio.get_running_loop().run_in_executor(executor, partial_func)
        except Exception as e:
            self._exception = e