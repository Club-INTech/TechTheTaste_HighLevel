from lpastarProcess.GAgent import GAgent
from lpastarProcess.ASensor import ASensor
from lpastarProcess.GMap import GMap
from typing import Type, Tuple, Dict, Iterable, List, Any
from lpastarProcess.pf_exceptions import MapInitializationException
from lpastarProcess.pf_exceptions import PathDoesNotExistException
from lpastarProcess.pf_exceptions import TimeoutException
from lpastarProcess.pf_exceptions import EmptyQueueException
import time
from lpastarProcess.PriorityQueue import PriorityQueue
import collections

from params import paramlpastar 


class LPAStarPathFinder:

    """ A class which implements LPA* algorithm and method
        which is responsible to rescan the environment with
        a sensor and run execution of agent's movement method.

    Attributes
    ----------
    agent: GAgent
        Agent, which executes movement orders of path finding.
    sensor: ASensor
        Sensor used to scan and rescan the map.
    period: int
        Map update period.
    infinity: int
        The "sufficient" modelization of infinity according to
        the graph nodes number.
    goal: Tuple[int, int]
        The goal vertex of the path finding.
    start: Tuple[int, int]
        The start vertex of the path finding.
    map: GMap
        A map representation as a graph containing
        the list of the obstacles.
    g: List[List[int]]
        g-values used to store the shortest distance
        from start to each vertex.
    rhs: List[List[int]]
        rhs-values used to update g-values. rhs-values are
        a one step look up which uses g-values.
    discover_order: PriorityQueue
        A priority queue used to store vertices to discover
        ordered by (min(g(s), rhs(s)) + h(s, goal), min(g(s), rhs(s))).
        
        
    Methods
    -------

    __shrink_path(model_path):
        Takes model_path and adds only key vertices in each path
        direction to avoid agent movements to be jerky.     
    __calculate_key(i, j):
        Calculates the key of vertex associated to the case
        (i, j) to insert it in priority queue.
    __update_vertex(v):
        Updates the rhs-value of the vertex and reinserts
        it in priority queue with new key if necessary.
    __pause():
        Pauses the exectuion of path finding and map update.
    __param_getter(param_name, params):
        Helper function, which allows to get
        information from a dictionary given in parameters.
    reset(goal):
        Resets start vertex, goal vertex, priorty_queue,
        g-values and rhs-values.
    find_path(goal):
        Entry point function which is responsible to rescan
        map, recalculate optimal path if necessary and update agent.
    compute_shortest_path():
        Computes the shortest path using the advantages of LPA* algorithm.

    """

    def __init__(self,
                 agent = GAgent,
                 sensor = ASensor,
                 params = paramlpastar): #Dict[str, int]
        """ Uses __param_getter method to extract data from dictionary.
        Initializes agent and sensor.

        Args:
            agent (Type[GAgent]):
                An agent which executes path finding movement commands.
            sensor (Type[ASensor]):
                A sensor which is used to scan the map.
            params (Dict[str, int]):
                A dictionary with attributes to initialize.
        """
        self.agent = agent
        self.sensor = sensor

        self.map = GMap(params, obstacles=[])
        self.period = self.__param_getter("period", params)
        self.infinity = 2 * self.map.obstacle_case_value * \
            (self.map.rows * self.map.columns ) ** 2
        self.timeout = self.__param_getter("timeout", params)

        self.goal = None
        self.start = None

        self.g = [[self.infinity for _ in range(self.map.columns)]
                  for _ in range(self.map.rows)]

        self.rhs = [[self.infinity for _ in range(self.map.columns)]
                    for _ in range(self.map.rows)]

        self.discover_order = PriorityQueue()

    def reset(self, goal: Tuple[float, float], Xrobot, Yrobot) -> None:
        """ Resets g-values and rhs-values. Initializes start and goal
            positions for the algorithm.

        Args:
            goal (Tuple[float, float]):
                The goal vertex
        """

        self.g = [[self.infinity for _ in range(self.map.columns)]
                  for _ in range(self.map.rows)]

        self.rhs = [[self.infinity for _ in range(self.map.columns)]
                    for _ in range(self.map.rows)]

        self.discover_order = PriorityQueue()
        
        self.goal = self.map.coors_to_indexes(*goal)
        x, y, _ = self.agent.get_position(self, Xrobot, Yrobot)
        i, j = self.map.coors_to_indexes(x, y) 
        self.start = (i, j)
        self.rhs[i][j] = 0 
        self.discover_order.insert((self.__calculate_key(i, j)), (i, j))


    def find_path(self, goal: Tuple[float, float], CamMat_Lpastar_pipeLpastar, lpastar_main_pipeLpastar, Xrobot, Yrobot) -> None:
        """ Entry point function which is responsible to rescan map,
            recalculate optimal path if necessary and update agent.
            First, it calls reset, after that it calls sensor's scan function,
            converts obstacles to its graph representation and compares them
            to the previous obstacles. If there is any changes, vertex with
            changed cost are updated and the path is recalculated.
            The path is then shrunk and provided to the agent worker process.

        Args:
            goal (Tuple[float, float]):
                The goal vertex.
        """
        # Reset of rhs-values, g-values, start and goal.
        self.reset(goal, Xrobot, Yrobot)
        begin = time.time_ns()
        while True: 
            # Break if timeout has occured
            if time.time_ns() - begin > (self.timeout * 1e9):
                raise TimeoutException("Timeout for \
                                        find_path has been reached")

            # Break if the agent has reached the goal.
            x, y, _ = self.agent.get_position(self, Xrobot, Yrobot) 
            if (x - goal[0]) ** 2 + (y - goal[1]) \
               <= (self.map.get_resolution() ** 2):
                self.agent.stop_trajectory(self,lpastar_main_pipeLpastar)
                break

            # Sensor scan.
            current_obstacles = self.map.get_obstacles() 
            new_obstacles = self \
                .map \
                .convert_obstacles_to_graph(
                                self
                                .sensor
                                .scan(self, conn_sensor = CamMat_Lpastar_pipeLpastar,origin=self.agent.get_position(self, Xrobot, Yrobot)))
            # If there is difference between previous
            # obstacles and current obstacles.
            if not collections.Counter(current_obstacles) \
                    == collections.Counter(new_obstacles):
                self.map.set_obstacles(new_obstacles)

                # Update vertices with changed cost.
                for obstacle in new_obstacles:
                    if obstacle not in current_obstacles:
                        self.__update_vertex(obstacle)

                for obstacle in current_obstacles:
                    if obstacle not in new_obstacles:
                        self.__update_vertex(obstacle)

                try:
                    
                    # Compute path and shrink it.
                    model_path = self.compute_shortest_path(Xrobot, Yrobot)
                    shrunk_path, shrunk_vertex_path = self.__shrink_path(model_path)
                    #real_path = map(
                    #    lambda point: self.map.indexes_to_coors(*point),
                    #    shrunk_path)

                    #self.agent.follow_trajectory(real_path)
                    
                    #conn.send(model_path[0]) #renvoie chaque position
                    #conn.send(shrunk_path[0]) #renvoie seulement les positions qui changent
                    lpastar_main_pipeLpastar.send(shrunk_vertex_path[1]) #le prochain step
                    break
                except PathDoesNotExistException:
                    self.__pause()

            # Pause.
            #self.__pause()

        # Clean up.
        #if self.agent.worker.is_alive():
        #    self.agent.worker.kill()
        #    self.agent.stop(lpastar_main_pipeLpastar)

    def __shrink_path(self,
                      model_path: List[Tuple[int, int]]) \
            -> Iterable[Tuple[int, int]]:
        """ Takes model_path and adds only key vertices in each
            path direction to avoid agent movements to be jerky.
            Adds only vertices that change agent's direction.

        Args:
            model_path (Iterable[Tuple[int, int]]):
                A path to shrink.

        Returns:
            Iterable[Tuple[int, int]]: Shrunk path.
        """
        shrunk_path = [model_path[0]]

        if len(model_path) > 2:
            direction = abs(model_path[0][0] - model_path[1][0]) + \
                        2 * abs(model_path[0][1] - model_path[1][1])
            for i in range(1, len(model_path)):
                tmp = direction
                direction = abs(model_path[i-1][0] - model_path[i][0]) + \
                    2 * abs(model_path[i-1][1] - model_path[i][1])
                if tmp != direction:
                    shrunk_path.append(model_path[i-1])
            shrunk_path.append(model_path[len(model_path) - 1])
        else:
            shrunk_path = model_path
            
        shrunk_vertex_path = [model_path[0]]
        for i in range(len(shrunk_path)-1):
            if shrunk_path[i][0] == shrunk_path[i+1][0]:
                dx = 0 
                dy = shrunk_path[i+1][1]-shrunk_path[i][1]
            elif shrunk_path[i][1] == shrunk_path[i+1][0]:
                dx = shrunk_path[i+1][0]-shrunk_path[i][0]
                dy = 0 
            else :
                dx = shrunk_path[i+1][0]-shrunk_path[i][0]
                dy = shrunk_path[i+1][1]-shrunk_path[i][1]
            shrunk_vertex_path.append([dx,dy])

        return shrunk_path, shrunk_vertex_path

    def __calculate_key(self, i: int, j: int) -> Tuple[int, int]:
        """ Calculates the key of vertex associated to the
            case (i, j) to insert it in priority queue.

        Args:
            i (int):
                first index of the vertex
            j (int):
                second index of the vertex

        Returns:
            Tuple[int, int]: A key used to insert vertex to the priority queue
        """
        #print(i,j)
        return min(self.g[i][j], self.rhs[i][j]) + \
                self.map.get_heurisitcs_cost((i, j),
                                         self.goal), min(self.g[i][j],
                                                         self.rhs[i][j])

    def __update_vertex(self, v: Tuple[int, int]) -> None:
        """ Updates the rhs-value of the vertex and reinserts it
            in priority queue with new key if necessary. The rhs-value
            of the vertex is updated according to the LPA* algorithm
            rhs-formula. You can find it in README of the repository.

        Args:
            v (Tuple[int, int]):
                A vertex to update.
        """
        i, j = v
        vertex = j,i
        #print(v)
        
        if vertex != self.start and i < len(self.rhs) and j < len(self.rhs[0]):
            self.rhs[i][j] = min(list(map(lambda x: self.g[x[0]][x[1]]
                                          + self.map.get_transition_cost(x, v),
                                          self.map.get_neighbours(v)
                                          )))
        self.discover_order.remove(v)
        if i < len(self.rhs) and j < len(self.rhs[0]) and self.g[i][j] != self.rhs[i][j]:
            self.discover_order.insert(self.__calculate_key(i, j), v)

    def compute_shortest_path(self, Xrobot, Yrobot) -> List[Tuple[int, int]]:
        """ Computes the shortest path using the advantages of
            LPA* algorithm. While the distance to the goal vertex
            (g-value) is not optimal and can be updated (g-value
            is different from rhs-value) we update the g-value of
            the vertex on the top of the priorirty queue and then
            we update its neighbours.

        Raises:
            PathDoesNotExistException: Raises if there is no path
            from start to goal.

        Returns:
            Iterable[Tuple[int, int]]: Returns the path where each
            two consecutive points are neigbours.
        """
        while ((self.discover_order.top_key()
                < self.__calculate_key(*self.goal)) or
                (self.rhs[self.goal[0]][self.goal[1]]
                    != self.g[self.goal[0]][self.goal[1]])):
            v = None
            try:
                v = self.discover_order.pop()
            except EmptyQueueException:
                break
            i, j = int(v[1][0]), int(v[1][1])
            v = i,j
            if self.g[i][j] > self.rhs[i][j]:
                self.g[i][j] = self.rhs[i][j]
                for neighbour in self.map.get_neighbours(v):
                    self.__update_vertex(neighbour)
            else:
                self.g[i][j] = self.infinity
                for neighbour in self.map.get_neighbours(v):
                    self.__update_vertex(neighbour)
                self.__update_vertex(v)

        if self.g[self.goal[0]][self.goal[1]] == self.infinity:
            raise PathDoesNotExistException("Cannot go from "
                                            + str(self.start)
                                            + " to "
                                            + str(self.goal))

        s = self.goal
        cur_vertex = self.map.coors_to_indexes(self.agent.get_position(self, Xrobot, Yrobot)[0],
                                               self.agent.get_position(self, Xrobot, Yrobot)[1])
        path = [s]
        while s != cur_vertex:
            neighbours = self.map.get_neighbours(s)
            pred = neighbours[0]
            min_pred = self.g[pred[0]][pred[1]] + \
                self.map.get_transition_cost(pred, s)
            for neighbour in neighbours:
                x = self.g[neighbour[0]][neighbour[1]] + \
                    self.map.get_transition_cost(neighbour, s)
                if x < min_pred:
                    min_pred = x
                    pred = neighbour
            path.insert(0, pred)
            s = pred

        return path

    def __pause(self) -> None:
        """ Pauses current process for **period** milliseconds
        """
        time.sleep(self.period / 1000.0)

    def __param_getter(self, param_name: str, params: Dict[str, Any]) -> Any:
        """ A function which is used to extract data
            from dictionary and verify that all required
            arguments have been provided.

        Args:
            param_name (str):
                A name of an argument to extract
            params (Dict[str, Any]):
                A dictionary to extract from

        Raises:
            MapInitializationException: Occurs when the
            required argument is missing

        Returns:
            Any: A value extracted from **params**
            associated to the key **param_name**
        """
        if param_name in params.keys():
            return params[param_name]
        raise MapInitializationException("Parameter required, \
                        but not provided: " + param_name)
