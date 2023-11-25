from dependency_graph.node import Node
from enum import Enum
from typing import Callable, Any, Optional, Dict
from util.async_timing import async_timed
from concurrent.futures import ProcessPoolExecutor, Future
from functools import partial
from application.TAGApplication import TAGApplication
import asyncio


class ExecutionStatus(Enum):
    TO_EXECUTE = 1
    EXECUTING = 2
    EXECUTED = 3


class ExecutableNode(Node):
    def __init__(self, name: str, task: Callable[..., Any]):
        super().__init__(name)
        self._task = task
        self._execution_status = ExecutionStatus.TO_EXECUTE
        self.execute = async_timed(self.name)(self.execute)
        
    def __str__(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return self._name 
    

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
    
    async def execute(self, shared_result: Optional[Dict[str, Future[Any]]]=None):
        if shared_result:
            dependency_results = {dependency.name: shared_result[dependency.name].result() for dependency in self.dependencies}
        else:
            dependency_results = {}

        if asyncio.iscoroutinefunction(self._task):
            result = await self._task(**dependency_results)
        else:
            with ProcessPoolExecutor() as executor:
                partial_func = partial(self._task, **dependency_results)
                result = await asyncio.get_running_loop().run_in_executor(executor, partial_func)
        self._execution_status = ExecutionStatus.EXECUTED
        return result