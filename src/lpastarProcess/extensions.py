from abc import abstractmethod
from typing_extensions import Protocol, TypeVar, Any

class Comparable(Protocol):

    @abstractmethod
    def __lt__(self, other: Any) -> bool:
        pass


comparable_t = TypeVar("comparable_t", bound=Comparable)
