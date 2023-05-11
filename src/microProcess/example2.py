import BT as BT
import random
import time
from datetime import datetime
from datetime import timedelta
from rich.console import Console
from rich import print


class Problem:
    """
    Represents a problem scenario.
    """

    def __init__(self):
        self.start_value = 10
        self.state = [0, 0, 0, 0, 0, 0, self.start_value]
        self.position = 1
        self.loaded = False


problem = Problem()


def display():
    """
    Displays the current state of the problem.
    """
    print()
    print("Loaded=", problem.loaded)
    print("\t".join([str(elt) for elt in problem.state]))
    print("\t" * (problem.position - 1) + "X")


def tache_terminee():
    """
    Checks if the task is completed.
    """
    return problem.state[-1] == 0 and not problem.loaded


def je_suis_charge():
    """
    Checks if the problem is in the loaded state.
    """
    return problem.loaded


def action_chargement():
    """
    Performs the loading action.
    """
    print("Chargement")
    if problem.position == len(problem.state):
        problem.loaded = True
        problem.state[-1] -= 1
    else:
        problem.position += 1
    return True


def action_dechargement():
    """
    Performs the unloading action.
    """
    print("Dechargement")
    if problem.position == 1:
        problem.loaded = False
        problem.state[0] += 1
    else:
        problem.position -= 1
    return True


c_tache_terminee = BT.ConditionNode("Tache_Terminee", callback=tache_terminee)
c_je_suis_charge = BT.ConditionNode("Je_Suis_CHarge", callback=je_suis_charge)

a_chargement = BT.ActionNode("Chargement", callback=action_chargement)
a_dechargement = BT.ActionNode("Dechargement", callback=action_dechargement)

seq1 = BT.SequenceNode("Seq1", [c_je_suis_charge, a_dechargement])

fal1 = BT.FallbackNode("Terrassement", [c_tache_terminee, seq1, a_chargement])

root = fal1
perturbation = False
BT.print(root.__str__())

while True:
    display()
    result = fal1.tick(verbose=False)
    print(f"Result: {result}")
    time.sleep(0.05)

    if perturbation and random.random() > 0.97:
        problem.state[-1] += 1
