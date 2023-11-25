from abc import ABC, abstractmethod
from typing import Set

class Node(ABC):
    def __init__(self, name: str):
        self._name = name
        self.dependencies: Set['Node'] = set()
        self.dependents: Set['Node'] = set()
        
    def __str__(self) -> str:
        return self._name
    
    def __repr__(self) -> str:
        raise NotImplementedError
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    @abstractmethod
    def executed(self) -> bool:
        raise NotImplementedError
    
    def add_dependency(self, dependency: 'Node'):
        self.dependencies.add(dependency)
        dependency.dependents.add(self)

    def dependency_count(self, dependency: 'Node'):
        return len(self.dependencies)
    
    def remove_dependency(self, dependency: 'Node'):
        self.dependencies.remove(dependency)
        dependency.dependents.remove(self)

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

    