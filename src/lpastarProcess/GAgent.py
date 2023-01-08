import multiprocessing as mp
from typing import Iterable, Tuple

class GAgent:

    """ A class which contains robot's methods to implement for path finding.
    Your robot class must inherit from this class and override get_position,
    move and stop methods.

    Attributes
    ----------
    worker: mp.Process
        A worker process to run agent's movement methods

    Methods
    -------
    
    get_position():
        Retreives the position  of the agent in **[x, y, alpha]** format,
        where **(x, y)** are the coordinates of the agent and **alpha**
        is its orientation.

    follow_trajectory(points):
        Makes the agent follow the trajectory. Must use a worker
        process to execute the path.

    move(x, y):
        Moves the agent to (x,y).

    stop():
        Stops the agent.
    """


    def __init__(self):
        """ Initializes robot's worker process to None.
        """
        self.worker = None
        self.parent = None
        self.child = None
        
    def follow_trajectory(self, points: Iterable[Tuple[float, float]]) -> None:
        """ Makes an agent follow a trajectory passed in parameters.
        Creates an auxiliary function which is run in the worker process.
        Uses move function.

        Args:
            points (Iterable[Tuple[float, float]]):
                A trajectory to follow. Each point is a tuple
                of the next position to go to.
        """
        
        if self.worker is not None and self.worker.is_alive():
            self.parent.send(points)
            return


        def follow(conn, _points): 
            _points_cp = _points
            i = 0

            while True:
                if conn.poll(): 
                    _points_cp = conn.recv()
                    i = 0 
                self.move(*_points_cp[i]) 
                if i < len(_points_cp) - 1: 
                    i += 1

        self.parent, self.child = mp.Pipe() 
        self.worker = mp.Process(target=follow, args=(self.child, points, ))
        self.worker.start()
    
    def stop_trajectory(self,conn) -> None: 
        """ Prevents agent from continuing the trajectory. Kills
        the worker process to stop giving movement commands. Sends
        a stop command to the agent.
        """
        self.worker.terminate()
        self.parent.close()
        self.child.close()
        self.stop(conn)
        
    def get_position(self,micro1_lpastar_pipeLpastar) -> Tuple[float, float, float]:
        """ Gets agent's position.

        Returns:
            Tuple[float, float, float]: The position of the agent
            in **[x, y, alpha]** format, where **(x, y)** are the
            coordinates of the agent and **alpha** is its orientation
        """
        
        micro1_lpastar_pipeLpastar.send("Resquest position")
        
        position = micro1_lpastar_pipeLpastar.recv() #[current position, [obstacle]]
        return position
    
    def move(self, x: float, y: float, positions) -> None:
        """ Moves agent to **(x, y)**

        Args:
            x (float):
                The x-coordinate to move to
            y (float):
                The y-coordinate to move to
        """
        x0,y0,alpha0 = GAgent.get_position(positions)
        dx,dy = x0 - x, y0 - y
        return dx, dy
    
    def stop(self,conn) -> None:
        """ Stops all movements of the agent
        """
        conn.send(1)
        pass
