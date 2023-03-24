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
        
    stop_trajectory():
        Prevents agent from continuing the trajectory. Kills
        the worker process to stop giving movement commands. Sends
        a stop command to the agent.


    stop():
        Stops the agent.
    """


    def __init__(self):
        """ Initializes robot's worker process to None.
        """
        self.worker = None
        self.parent = None
        self.child = None
    
    def stop_trajectory(self,conn) -> None: 
        """ Prevents agent from continuing the trajectory. Kills
        the worker process to stop giving movement commands. Sends
        a stop command to the agent.
        """
        self.stop(self,conn)
        
    def get_position(self, Xrobot, Yrobot) -> Tuple[float, float, float]:
        """ Gets agent's position.

        Returns:
            Tuple[float, float, float]: The position of the agent
            in **[x, y, alpha]** format, where **(x, y)** are the
            coordinates of the agent and **alpha** is its orientation
        """
        return Xrobot, Yrobot, 10
    
    
    def stop(self,conn) -> None:
        """ Stops all movements of the agent
        """
        conn.send(1)
        pass
