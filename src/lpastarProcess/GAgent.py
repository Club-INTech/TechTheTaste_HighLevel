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
                if conn.poll(): #retour vrai ou faux selon si des données sont disponible à la lecture
                    _points_cp = conn.recv() #Renvoie un objet envoyé depuis l'autre extrémité de la connexion en utilisant send
                    i = 0 
                self.move(*_points_cp[i]) # *: permet donner le premier élement de la liste des points | [i] de donner x et y pour move
                if i < len(_points_cp) - 1: #incrémente i de 1 afin que le robot se déplace à travers chaque point
                    i += 1

        self.parent, self.child = mp.Pipe() #Création d'un tube où parent reçoit des données et chil envoie des données
        self.worker = mp.Process(target=follow, args=(self.child, points, )) #Crée un process où target est la fonction qui va run et args donne les données pour le process
        self.worker.start() #Commence le processus 
    
    #Fonction pour arrêter le robot dans sa trajectoire
    def stop_trajectory(self,conn) -> None: 
        """ Prevents agent from continuing the trajectory. Kills
        the worker process to stop giving movement commands. Sends
        a stop command to the agent.
        """
        self.worker.terminate() #Arrête le processus de worker
        self.parent.close() #Souvent après terminate et assure que les ressources sont libérés 
        self.child.close()
        self.stop(conn)
        
    #Fontion pour obtenir la position du moment du robot 
    def get_position(self,conn_sensor) -> Tuple[float, float, float]:
        """ Gets agent's position.

        Returns:
            Tuple[float, float, float]: The position of the agent
            in **[x, y, alpha]** format, where **(x, y)** are the
            coordinates of the agent and **alpha** is its orientation
        """
        positions = conn_sensor.recv() #renvoie une liste [position actuelle, [obstacles]]
        return positions[0]
    
    #Fonction pour déplacer le robot aux coordonnées (x,y)
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
    
    #Fonction qui arrête net 
    def stop(self,conn) -> None:
        """ Stops all movements of the agent
        """
        conn.send(1)
        pass
