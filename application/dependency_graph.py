from typing import Set, Callable, Any
from enum import Enum


class ExecutionStatus(Enum):
    TO_EXECUTE = 1
    EXECUTING = 2
    EXECUTED = 3


class Node:
    def __init__(self, name: str, task: Callable[..., Any]):
        if not callable(task):
            raise Exception(f"Task must be callable, not {task}")
        self.name = name
        self.task = task
        self.dependencies: Set['Node'] = set()
        self.dependents: Set['Node'] = set()
        self.execution_status: ExecutionStatus = ExecutionStatus.TO_EXECUTE

    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return self.name
    
    # TODO: better type annotation?
    def __call__(self, *args: ..., **kwargs: ...):
        return self.task(*args, **kwargs)
    
    @property
    def cleared(self) -> bool:
        return self.execution_status == ExecutionStatus.EXECUTED

    def add_dependency(self, dependency: 'Node'):
        self.dependencies.add(dependency)
        dependency.dependents.add(self)

    def dependecy_count(self) -> int:
        return len(self.dependencies)
    
    def remove_dependency(self, dependency: 'Node'):
        if dependency in self.dependencies:
            self.dependencies.discard(dependency)
            dependency.dependents.discard(self)

    def clear(self):
        self.execution_status = ExecutionStatus.EXECUTED

    def ready_to_execute(self) -> bool:
        return all(dependency.cleared for dependency in self.dependencies) and self.execution_status == ExecutionStatus.TO_EXECUTE

    def get_dependencies(self):
        visited: Set['Node'] = set()
        self._dfs_dependency(visited)
        visited.discard(self)
        return visited
    
    def get_dependents(self):
        visited: Set['Node'] = set()
        self._dfs_dependent(visited)
        visited.discard(self)
        return visited
    
    def get_top_dependent(self):
        max_dependencies = 0
        top_node = None
        to_visit = [self]
        visited: Set['Node'] = set()

        while to_visit:
            node = to_visit.pop()
            if node not in visited:
                visited.add(node)
                dependency_count = len(node.get_dependencies())
                if dependency_count > max_dependencies:
                    max_dependencies = dependency_count
                    top_node = node
                to_visit.extend(node.dependents)
        return top_node

    def _dfs_dependency(self, visited: Set['Node']):
        visited.add(self)
        for node in self.dependencies:
            if node not in visited:
                node._dfs_dependency(visited)

    def _dfs_dependent(self, visited: Set['Node']):
        visited.add(self)
        for node in self.dependents:
            if node not in visited:
                node._dfs_dependent(visited)