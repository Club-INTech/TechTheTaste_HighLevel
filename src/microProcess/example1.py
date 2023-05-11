import BT
import random
import time
import logging
from logging import getLogger
from rich.logging import RichHandler

# Set up logger
logger = logging.getLogger(__name__)
logger.addHandler(RichHandler())

# Definitions des actions

def action1():
    """
    Executes action 1.
    """
    success = random.random() < 0.6
    print("1")
    return success

def action2():
    """
    Executes action 2.
    """
    success = random.random() < 0.1
    print("2")
    return success


a1 = BT.ActionNode("action1", callback=action1)
a2 = BT.ActionNode("action2", callback=action2)

# Definitions des conditions

def condition1():
    """
    Checks condition 1.
    """
    return random.random() < 0.3

def condition2():
    """
    Checks condition 2.
    """
    return random.random() < 0.8


c1 = BT.ConditionNode("condition1", callback=condition1)
c2 = BT.ConditionNode("condition2", callback=condition2)

# Definition de l'arbre

seq1 = BT.SequenceNode("Seq1", [c1, a1])
seq2 = BT.SequenceNode("Seq2", [c2, a2])

fallback = BT.FallbackNode("Fal1", [seq1, seq2])

# Definition de la racine
root = fallback

# Pour afficher l'arbre
BT.print(root.__str__())

# Boucle principale
while True:
    result = root.tick(verbose=True)
    time.sleep(0.5)
