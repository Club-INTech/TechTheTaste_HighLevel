from abc import abstractmethod
from typing_extensions import Protocol, TypeVar, Any
#Importation de typing :
#Protocol : la classe de de base des classes de protocoles 
#TypeVar : Type variable | ('T') : tout type | ('S',bound=str) sous type de str | ('A', str, bytes) ne peut que être des str ou bytes
#Any : Tous les types sont compatibles avec Any

#Une classe est une "Abstract class"
#Une méthode abstraite n'est pas une méthode qui est déclaré mais n'est pas implémenté.
#Une méthode abstraite doit être implémenté par sa sous-classe

class Comparable(Protocol):

    @abstractmethod
    def __lt__(self, other: Any) -> bool:
        pass


comparable_t = TypeVar("comparable_t", bound=Comparable)
