__all__ = ["colours", "fonts"]

from typing import Iterator, Iterable, TypeVar, override, Generic
from numbers import Complex

from collections import deque

Number = TypeVar("Number", int, float)
DataType = TypeVar("DataType")

class queue(Generic[DataType]):
    """ A simple queue class """
    def __init__(self) -> None:
        """ Initialise queue """
        self.data: deque[DataType] = deque()  # double-ended queue

    @override
    def __repr__(self) -> str:
        """ String representation of queue 

            Returns string of list of data in queue
        """
        return str(list(self.data))
 

    def __iter__(self) -> Iterator[DataType]:
        """ Iterator for queue """
        return iter(self.data)


    def push(self, x:DataType) -> None:
        """ Push item onto back of queue """
        self.data.append(x)


    def pop(self) -> DataType:
        """ Pop item from front of queue """
        return self.data.popleft()


class stack(queue[DataType]):
    """ A simple stack class """
    @override
    def pop(self) -> DataType:
        """ Pop item from top of stack """
        return self.data.pop()
    

def manhattan(a:tuple[Number, Number], b:tuple[Number, Number]) -> Number:
    """ Compute Manhattan distance between two (x, y) locations """
    ax, ay = a  # (x, y)
    bx, by = b  # (x, y)
    return abs(bx-ax) + abs(by-ay)