from abc import abstractmethod
import typing_extensions
from typing_extensions import Protocol, TypeVar, Any

#for PriorityQueue.py

class Comparable(Protocol):

    @abstractmethod
    def __lt__(self, other: Any) -> bool:
        pass


comparable_t = TypeVar("comparable_t", bound=Comparable)
