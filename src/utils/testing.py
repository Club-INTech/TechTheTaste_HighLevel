import random
import time

def generate_obstacles() :
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