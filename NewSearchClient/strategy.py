import sys
from abc import ABCMeta, abstractmethod
from collections import deque
from time import perf_counter

import configuration as config
from heuristic import Heuristic
from state import State


class Strategy(metaclass=ABCMeta):
    def __init__(self):
        self.explored = set()
        self.start_time = perf_counter()
    
    def add_to_explored(self, state: 'State'):
        self.explored.add(state)
    
    def is_explored(self, state: 'State') -> 'bool':
        return state in self.explored
    
    def explored_count(self) -> 'int':
        return len(self.explored)
    
    def time_spent(self) -> 'float':
        return perf_counter() - self.start_time
    
    def search_status(self) -> 'str':
        return '#Explored: {:6}, #Frontier: {:6}, #Generated: {:6}, Time: {:3.2f} s, Alloc: {:4.2f} MB, MaxAlloc: {:4.2f} MB'.format(self.explored_count(),
                                                                                                                                     self.frontier_count(),
                                                                                                                                     self.explored_count() + self.frontier_count(),
                                                                                                                                     self.time_spent(),
                                                                                                                                     config.get_memory_usage(),
                                                                                                                                     config.max_usage)
    
    @abstractmethod
    def get_and_remove_leaf(self) -> 'State': raise NotImplementedError
    
    @abstractmethod
    def add_to_frontier(self, state: 'State'): raise NotImplementedError
    
    @abstractmethod
    def in_frontier(self, state: 'State') -> 'bool': raise NotImplementedError
    
    @abstractmethod
    def frontier_count(self) -> 'int': raise NotImplementedError
    
    @abstractmethod
    def frontier_empty(self) -> 'bool': raise NotImplementedError
    
    @abstractmethod
    def __repr__(self): raise NotImplementedError


class StrategyBFS(Strategy):
    def __init__(self):
        super().__init__()
        self.frontier = deque()
        self.frontier_set = set()
    
    def get_and_remove_leaf(self) -> 'State':
        leaf = self.frontier.popleft()
        self.frontier_set.remove(leaf)
        return leaf
    
    def add_to_frontier(self, state: 'State'):
        self.frontier.append(state)
        self.frontier_set.add(state)
    
    def in_frontier(self, state: 'State') -> 'bool':
        return state in self.frontier_set
    
    def frontier_count(self) -> 'int':
        return len(self.frontier)
    
    def frontier_empty(self) -> 'bool':
        return len(self.frontier) == 0
    
    def __repr__(self):
        return 'Breadth-first Search'


class StrategyDFS(Strategy):
    def __init__(self):
        super().__init__()
        self.frontier = list()
        self.frontier_set = set()
    
    def get_and_remove_leaf(self) -> 'State':
        leaf = self.frontier.pop()
        self.frontier_set.remove(leaf)
        return leaf
    
    def add_to_frontier(self, state: 'State'):
        self.frontier.append(state)
        self.frontier_set.add(state)
    
    def in_frontier(self, state: 'State') -> 'bool':
        return state in self.frontier_set
    
    def frontier_count(self) -> 'int':
        return len(self.frontier)
    
    def frontier_empty(self) -> 'bool':
        return len(self.frontier) == 0
    
    def __repr__(self):
        return 'Depth-first Search'


class StrategyBestFirst(Strategy):
    def __init__(self, heuristic: 'Heuristic'):
        super().__init__()
        self.heuristic = heuristic
        self.frontier = PriorityQueue(heuristic)
        self.frontier_set = set()
    
    def get_and_remove_leaf(self) -> 'State':
        leaf = self.frontier.delete()
        self.frontier_set.remove(leaf)
        return leaf
    
    def add_to_frontier(self, state: 'State'):
        self.frontier.insertInOrder(state)
        self.frontier_set.add(state)
        while self.frontier_count() > 100:
            leaf = self.frontier.deleteFromTail()
            self.frontier_set.remove(leaf)
    
    def in_frontier(self, state: 'State') -> 'bool':
        return state in self.frontier_set
    
    def frontier_count(self) -> 'int':
        return self.frontier.length()
    
    def frontier_empty(self) -> 'bool':
        return self.frontier.length() == 0
    
    def __repr__(self):
        return 'Best-first Search using {}'.format(self.heuristic)


# Structure to save states sorted by their heuristic 'f' value.
class PriorityQueue(object): 
    def __init__(self, heuristic: 'Heuristic'): 
        self.queue = [] 
        self.heuristic = heuristic
  
    def __str__(self): 
        return ' '.join([str(i) for i in self.queue]) 
  
    # Check if the queue is empty.
    def isEmpty(self): 
        return len(self.queue) == [] 
    
    # Check length of the queue.
    def length(self): 
        return len(self.queue) 
  
    # Insert an element in the queue taking into account its priority.
    def insertInOrder(self, data): 
        data.h = self.heuristic.f(data)
        try: 
            if len(self.queue) == [] :
                self.queue.append(data)
                return
            for i in range(len(self.queue)): 
                if data.h < self.queue[i].h: 
                    self.queue.insert(i, data) # +1 to insert after index
                    return
            self.queue.append(data)
            return    
        except IndexError: 
            print('Indexation error while trying to add a new item to the PriorityQueue for heuristics.', file=sys.stderr, flush=True)
            exit() 
  
    # Popping an element based on Priority.
    def delete(self): 
        item = self.queue[0] 
        del self.queue[0] 
        return item 
    
    # Deletes the least priority item
    def deleteFromTail(self):
        idx = self.length()-1
        item = self.queue[idx] 
        del self.queue[idx]
        return item
    
    #look at item at index i
    def peek(self, i): 
        
        if self.length() <=i:
            return "Queue does not have "+ str(i)+ " elements"
        else:
            s = self.queue[i]
            print("h value: "+str(s.h), file=sys.stderr, flush=True)
            return s
        
    def clearFrontier(self):
        self.queue = [] 
