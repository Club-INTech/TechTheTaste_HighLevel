import pytest
from typing import Tuple, List
import random
import time
# from math import sqrt
from lpastar_pf.pf_exceptions import ImpossibleTransitionException


def generate_obstacles() -> List[Tuple[float, float, float]]:
    obstacles = [(0.0, 1000.0, 24.0),
                 (1500.0, 0.0, 24.0),
                 (3000.0, 1000.0, 24.0),
                 (0.0, 2000.0, 24.0)]
    random.seed(time.time())
    for i in range(50):
        x = random.uniform(0.0, 3000.0)
        y = random.uniform(0.0, 2000.0)
        w = 50.0 * random.random()
        obstacles.append((x, y, w))
    return obstacles


@pytest.fixture
def mock_map():
    from ..GMap import GMap
    return GMap(
        params={
            "width": 3000,
            "height": 2000,
            "resolution": 5,
            "free_case_value": 1,
            "obstacle_case_value": 1000,
            "heuristics_multiplier": 1
        }, obstacles=generate_obstacles()
    )


def test_border_obstacles(mock_map):
    for i in range(2):
        assert (i, 200) in mock_map.obstacles
        assert (i, 200 - i) in mock_map.obstacles
        assert (i, 200 + i) in mock_map.obstacles
        assert (0, 200 + i) in mock_map.obstacles
    assert (3, 200) not in mock_map.obstacles
    assert (1, 205) not in mock_map.obstacles


def test_coors_to_indexes(mock_map):
    (i, j) = mock_map.coors_to_indexes(1456.25, 490.0)
    assert i == 291
    assert j == 98


def test_indexes_to_coors(mock_map):
    (x, y) = mock_map.indexes_to_coors(356, 123)
    assert x == 1780.0
    assert y == 615.0

# def test_transition_cost(mock_map):
#     for _ in range(1000):
#         i1 = random.randint(1, 600)
#         j1 = random.randint(1, 400)
#         i2 = i1 + random.randint(-1, 2)
#         j2 = j1 + random.randint(-1, 2)
#         s = mock_map.get_transition_cost((i1, j1), (i2, j2))

#         if (i1, j1) in mock_map.obstacles or (i2, j2) in mock_map.obstacles:
#             assert s == 1000.0
#         else:
#             assert s == sqrt(abs(i1 - i2) + abs(j1 - j2))


def test_impossible_transition_cost(mock_map):
    for _ in range(100):
        i1 = random.randint(0, 300)
        j1 = random.randint(0, 200)
        i2 = random.randint(302, 600)
        j2 = random.randint(202, 400)
        with pytest.raises(ImpossibleTransitionException):
            mock_map.get_transition_cost((i1, j1), (i2, j2))

obstacles = generate_obstacles()
print(obstacles)

