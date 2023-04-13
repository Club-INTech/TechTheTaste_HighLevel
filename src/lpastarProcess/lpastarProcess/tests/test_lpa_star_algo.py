from lpastar_pf import LPAStarPathFinder
import pytest
from typing import Tuple, List
import random
import time
# from math import sqrt
from lpastar_pf.pf_exceptions import ImpossibleTransitionException
import numpy as np


from email.policy import strict
from lpastar_pf import LPAStarPathFinder
from lpastar_pf.GAgent import GAgent
from lpastar_pf.ASensor import ASensor
from lpastar_pf.GMap import GMap


import numpy as np
import matplotlib.pyplot as plt


def generate_obstacles() -> List[Tuple[float, float, float]]:
    obstacles = [(0.0, 1000.0, 24.0),
                (1500.0, 0.0, 24.0),
                (3000.0, 1000.0, 24.0),
                (0.0, 2000.0, 24.0)]
    random.seed(time.time())
    for i in range(100):
        x = random.uniform(0.0, 3000.0)
        y = random.uniform(0.0, 2000.0)
        w = 50.0 * random.random()
        obstacles.append((x, y, w))
    return obstacles

lpastar = LPAStarPathFinder.LPAStarPathFinder(agent= GAgent, sensor=ASensor, params={
            "width": 3000,
            "height": 2000,
            "resolution": 50,
            "free_case_value": 1,
            "obstacle_case_value": 1000,
            "heuristics_multiplier": 1,
            "period" : 2,
            "timeout" : 10
            })

def mock_map():
    return GMap(
        params={
            "width": 3000, #colonne
            "height": 2000, #ligne
            "resolution": 50,
            "free_case_value": 1,
            "obstacle_case_value": 1000,
            "heuristics_multiplier": 1
        }, obstacles=generate_obstacles()
    )

def matrix_index(obstacles):
    matrix = np.zeros((int((3000/50)+ 1),int(2000/50)+ 1 )) #ligne puis colonne
    obstacles_index = mock_map().convert_obstacles_to_graph(obstacles=obstacles)
    
    for index in obstacles_index :
        x = index[0]
        y = index[1]
        matrix[x,y] = 1
    return matrix

child_Lpastar_conn = None
obstacles = generate_obstacles()
map = matrix_index(obstacles)

Positions = [(0,0,0), obstacles]
goal = ([1999, 2999]) #colonne puis ligne 
model_path, shrunk_path = lpastar.find_path(goal, child_Lpastar_conn, Positions)

print("######## model_path ########")
print(model_path)
print("######## shrunk_path #######")
print(shrunk_path)
#print("#########################")
#L =[model_path[i][1] for i in range(len(model_path))]
#print(L)
        
#print(model_path)
#print(shrunk_path)

for i in range(len(model_path)):
    y = model_path[i][0]
    x = model_path[i][1]
    map[x,y] = 0.5

plt.imshow(map)
plt.colorbar()
plt.show()