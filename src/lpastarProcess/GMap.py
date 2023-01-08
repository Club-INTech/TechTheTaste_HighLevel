from typing import Iterable, Dict, Tuple, Any
from lpastar_pf.pf_exceptions import MapInitializationException
from lpastar_pf.pf_exceptions import ImpossibleTransitionException
from math import sqrt


class GMap():
    """ A class that represents a map. User must provide attributes
    values in chosen units and respect the convention. This class
    allows to represent a 2D environment as a non-oriented graph
    where each vertex corresponds to the center of the square case
    with **resolution x resolution** dimensions. The adjacent cases
    are modelized by adjecent vertices.

    There is only 2 types of vertices: free vertices and obstacle
    vertices. We maintain only the list of obstacles and we use
    **get_transition_cost** to retreive the edge cost and
    **get_heuristics_cost** to retreive the heuristics cost.


    Attributes
    ----------
    width: int
        The width of the map.
    height: int
        The height if the map.
    resolution: int
        The dimension of the square case representable
        by a vertex.
    
    rows: int
        Number of cases' rows in map representation.
    columns: int
        Number of cases' columns in map representation.
    
      
    free_case_value: int
        A multiplier for a transition from free case
        to the another free case.
    obstacle_case_value: int
        A multiplier for a transition from or
        to the obstacle case.
    
    obstacles: Iterable[Tuple[int, int]]
        A list of obstacles represented by
        theirs indices **(i, j)**
    heuristics_multiplier: int
        A multiplier for a heuristics transition cost.
   
    Methods
    -------

    __param_getter(param_name, params):
        Helper function, which allows to get
        information from a dictionary given in parameters.
    
    coors_to_indexes(x, y):
        Helper function used to convert real
        life coordinates to their graph representation.
    indexes_to_coors(i, j):
        Helper function used to convert graph representation
        indices to the real life coordinates.
    
    convert_obstacles_to_graph(obstacles):
        Helper function which allows create graph representation
        obstacles from real life obstacles according
        to their width.
    
    get_transition_cost(_from, _to):
        Gets the edge cost from vertex **_from** to
        the vertex **_to**.
    get_neighbours(vertex):
        Gets neighbours of the **vertex**.
    get_heuristics_cost(_from, _to):
        Gets the heuristics cost from vertex
        **_from** to the vertex **_to**.
    get_resolution():
        Gets the resolution.
    get_obstacles():
        Gets all **obstacles**.
    set_obstacles(obstacles):
        Sets **obstacles**.
    """

    def __init__(self,
                 params: Dict[str, int],
                 obstacles: Iterable[Tuple[float, float, float]] = None
                 ) -> None:
        """ Uses __param_getter method to extract data from dictionary.
        Initializes obstacles if provided.

        Args:
            obstacles=None (Iterable[Tuple[float, float, float]]):
                A list of real life obstacles.
            params (Dict[str, int]):
                A dictionary with attributes to initialize.
        """
       
        self.width = self.__param_getter("width", params) 
        self.height = self.__param_getter("height", params)
        self.resolution = self.__param_getter("resolution", params)

        self.rows = int((self.height / self.resolution))
        self.columns = int((self.width / self.resolution))

        self.free_case_value = self.__param_getter("free_case_value", params)
        self.obstacle_case_value = self.__param_getter("obstacle_case_value",
                                                       params)

        # We must convert real life obstacles ([x, y, w])
        # to theirs graph representation ([i, j]).
        self.obstacles = self.convert_obstacles_to_graph(obstacles)

        self.heuristics_multiplier = self \
            .__param_getter("heuristics_multiplier",
                            params)

    def __param_getter(self, param_name: str, params: Dict[str, Any]) -> Any:
        """ A function which is used to extract data from
            dictionary and verify that all required arguments
            have been provided.

        Args:
            param_name (str):
                A name of an argument to extract.
            params (Dict[str, Any]):
                A dictionary to extract from.

        Raises:
            MapInitializationException: Occurs when the required
            argument is missing
            
        Returns:
            Any: A value extracted from **params**
            associated to the key **param_name**
        """

        
        if param_name in params.keys():
            return params[param_name]
        raise MapInitializationException(
            "Parameter required, but not provided: " + param_name) 

    
    def convert_obstacles_to_graph(self,
                                   obstacles:
                                   Iterable[Tuple[float, float, float]]
                                   ) -> Iterable[Tuple[int, int]]:
        """ Converts real life obstacles to theirs' graph representation.
            Obstacles' representations as graph have no width, they occupy
            only graph cases/vertices.

        Args:
            obstacles (Iterable[Tuple[float, float, float]]):
                Real life obstacles in **[x, y, w]** format,
                where **(x, y)** are obstacle's coordinates
                and **w** is its width

        Returns:
            Iterable[Tuple[int ,int]]: Graph representation of the obstacles.

        """
        model_obstacles = []
        for obstacle in obstacles:
            x = obstacle[0]
            y = obstacle[1]
            w = obstacle[2] / 2 

            square_left_i, square_top_j = self.coors_to_indexes(
                max(0.0, x - w),
                max(0.0, y - w))

            square_right_i, square_bottom_j = self.coors_to_indexes(
                min(self.width, x + w),
                min(self.height, y + w))

            for i in range(square_left_i, square_right_i + 1):
                for j in range(square_top_j, square_bottom_j + 1):
                    model_obstacles.append((i, j))

        return model_obstacles

    def coors_to_indexes(self, x: float, y: float) -> Tuple[int, int]:
        """ Converts real life coordinates to the indices of the graph's vertex

        Args:
            x (float):
                Real life x coordinate
            y (float):
                Real life y coordinate

        Returns:
            Tuple[int, int]: Indices of the graph's vertex
            which corresponds to the **(x, y)**
        """
        return int(x / self.resolution), int(y / self.resolution)
    
    #def listcoors_to_indexes(self, coors: Tuple[float,float]):
    #    listcoors = []
    #    for i in range(len(coors)):
    #        a = self.coors_to_indexes(coors[i][0],coors[i][1])
    #        listcoors.append(a)
    #    return listcoors

    def indexes_to_coors(self, i: int, j: int) -> Tuple[float, float]:
        """ Converts indices of the graph's vertex to the real life coordinates

        Args:
            i (int):
                First index of the vertex
            j (int):
                Second index of the vertex

        Returns:
            Tuple[float, float]: Real life coordinates
        """
        return float(i * self.resolution), float(j * self.resolution)

    def get_transition_cost(self,
                            _from: Tuple[int, int],
                            _to: Tuple[int, int]) -> float:
        """ Gets a transition cost between **_from** and **_to** vertex if
            and only if they are neighbours.

        Args:
            _from (Tuple[int, int]):
                A vertex to go from
            _to (Tuple[int, int]):
                A vertex to go to

        Raises:
            ImpossibleTransitionException: Exception occurs,
            when **_from** and **_to** are not neighbours.

        Returns:
            float: A transition cost from **_from** to **_to**
        """


        if abs(_from[0] - _to[0]) > 1 or abs(_from[1] - _to[1]) > 1:
            raise ImpossibleTransitionException("Impossible transition from ("
                                                + str(_from[0])
                                                + ","
                                                + str(_from[1])
                                                + ") to ("
                                                + str(_to[0])
                                                + ","
                                                + str(_to[1])) 

        if _to in self.obstacles or _from in self.obstacles: 
            return self.obstacle_case_value 
        else:
            return self.free_case_value * \
                sqrt(abs(_from[1] - _to[1]) +
                     abs(_from[0] - _to[0])) 


    def get_neighbours(self,
                       vertex: Tuple[int, int]) -> Iterable[Tuple[int, int]]:
        """ Gets all neighbours of the **vertex**

        Args:
            vertex (Tuple[int, int]):
                The vertex to get neighbours of

        Returns:
            Iterable[Tuple[int, int]]: Neighbours of the **vertex**
        """
        
        i,j = vertex
        neighbours = []
        


        if i - 1 >= 0: 
            neighbours.append((i-1, j))
            if j - 1 >= 0:
                neighbours.append((i-1, j-1))
            if j + 1 < self.columns :
                neighbours.append((i-1, j+1))
        if i + 1 < self.rows: 
            neighbours.append((i+1, j))
            if j - 1 >= 0:
                neighbours.append((i, j-1)) 
                neighbours.append((i+1, j-1)) 
            if j + 1 < self.columns: 
                neighbours.append((i, j+1)) 
                neighbours.append((i+1, j+1))
        
        
        """
        if i - 1 >= 0: #haut
            neighbours.append((i-1, j))
            if j - 1 >= 0: #haut/gauche
                neighbours.append((i-1, j-1))
            if j + 1 < self.columns : #haut/droite
                neighbours.append((i-1, j+1))
        if i + 1 < self.rows :
            neighbours.append((i+1,j))
            if j - 1 >=0 : #bas/gauche
                neighbours.append((i-1,i+1))
            if j + 1 < self.columns :
                neighbours.append((i+1,j+1))
        if j + 1 < self.columns :
            neighbours.append((i,j+1))
        if j - 1 >= 0 :
            neighbours.append((i,j-1))
        """    
        return neighbours
    

    def get_heurisitcs_cost(self,
                            _from: Tuple[int, int],
                            _to: Tuple[int, int]) -> float:
        """ Gets heuristics cost to go from **_from** to **_to**

        Args:
            _from (Tuple[int, int]):
                A vertex to go from
            _to (Tuple[int, int]):
                A vertex to go to

        Returns:
            float: The heuristics cost from **_from** to **_to**
        """
        return self.heuristics_multiplier * \
            sqrt(abs(_from[1] - _to[1]) ** 2 +
                 abs(_from[0] - _to[0]) ** 2) #flying distance * heuristics_multiplier 

    def get_resolution(self) -> int:
        """ Gets the resolution

        Returns:
            int: The resolution of the map
        """
        return self.resolution

    def get_obstacles(self) -> Iterable[Tuple[int, int]]:
        """ Gets the list of current obstacles on the map

        Returns:
            Iterable[Tuple[int, int]]: A list of obstacles
        """
        return self.obstacles

    def set_obstacles(self, _obstacles: Iterable[Tuple[int, int]]) -> None:
        """ Puts new list of obstacles on the map

        Args:
            _obstacles (Iterable[Tuple[int, int]]):
                A new list of obstacles to put on the map
        """
        self.obstacles = _obstacles
