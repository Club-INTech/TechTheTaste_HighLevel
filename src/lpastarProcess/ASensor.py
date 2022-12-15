from abc import ABC, abstractmethod
from typing import Iterable, Tuple

#importation de la library Abstract Base Classes: 
#Le module 'abc' permet donner les éléments pour créer des bases de classes abstraites personnalisées.
#'abc' permet de marquer les méthodes de la base comme abstraite
#La classe ABC permet de définir la base des classes abstraites
#ABC est un helper qui peut être utiliser à la place de abc.ABC


class ASensor(ABC):

    """ Abstract class ASensor that simulates any sensor.
    Your sensor class must inherit from it and override
    the scan methods.

    Methods
    -------
    scan(origin):
        Scans the environment and returns a list of
        absolute coordinates of obstacles.
    """
    

    #Entrée : Position du robot avec (x,y,alpha)
    #Sortie : Matrice de la map avec les obstacles 
    @abstractmethod
    def scan(self, origin: Tuple[float, float, float], conn_sensor) -> \
            Iterable[Tuple[float, float, float]]:
        """ Scans the environment according to the sensor
        position and returns a list of obstacles

        Args:
            origin (Tuple[float, float, float]):
                The position of the sensor in the **[x, y, alpha]** format,
                where  **(x, y)** are the coordinates of the sensor and
                **alpha** is its orientation. It is used to transform
                relative obstacles' coordinates to absolute coordinates
                compared to map's origin.

        Returns:
            Iterable[Tuple[float, float, float]]: An Iterable(list generally)
            of the obstacles in the **[x, y, w]** format, where **(x, y)** are
            the absolute coordinates of the center of an obstacle and **w**
            is its width
        """
        
        positions = conn_sensor.recv() # [position actuelle, [obstacles]]
        return positions[-1]
