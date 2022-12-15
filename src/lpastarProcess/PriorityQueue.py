from lpastar_pf.extensions import comparable_t
from lpastar_pf.pf_exceptions import EmptyQueueException
import heapq


class PriorityQueue:

    def __init__(self):
        self.h = []

    #Insert dans la liste h (key, value) avec key qui est la priorité 
    def insert(self, key: comparable_t, value: comparable_t):
        heapq.heappush(self.h, (key, value))

    #Enlève l'élement avec la plus petite priorité et la renvoie
    #Fonction utilisé dans remove
    def pop(self):
        if len(self.h) == 0: #test si la liste h est vide
            raise EmptyQueueException("Can't pop, the queue is empty")
        return heapq.heappop(self.h)

    #Renvoie la key qui a la plus petite priorité , c'est à dire le premier élement
    def top_key(self):
        if len(self.h) == 0:
            raise EmptyQueueException("Can't get top key, the queue is empty")
        return self.h[0][0]

    #Enlève value et la remplace par h[-1]
    def remove(self, value: comparable_t) -> None:
        pos = -1
        for i in range(len(self.h)): #i parcours la liste
            if self.h[i][1] == value: #Regarde value est dans la liste h 
                pos = i
                break

        if pos == -1: #Si value n'est pas dans la liste, le programme s'arrête
            return

        self.h[pos] = self.h[-1] #on remplace par la plus grande priorité 
        self.h.pop() #on enlève h[-1] qui est deux fois dans la liste
        heapq.heapify(self.h) #h est transformé en tas
