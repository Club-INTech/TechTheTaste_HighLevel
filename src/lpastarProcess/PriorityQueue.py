from lpastar_pf.extensions import comparable_t
from lpastar_pf.pf_exceptions import EmptyQueueException
import heapq


class PriorityQueue:

    def __init__(self):
        self.h = []

    def insert(self, key: comparable_t, value: comparable_t):
        heapq.heappush(self.h, (key, value))


    def pop(self):
        if len(self.h) == 0: 
            raise EmptyQueueException("Can't pop, the queue is empty")
        return heapq.heappop(self.h)


    def top_key(self):
        if len(self.h) == 0:
            raise EmptyQueueException("Can't get top key, the queue is empty")
        return self.h[0][0]


    def remove(self, value: comparable_t) -> None:
        pos = -1
        for i in range(len(self.h)): 
            if self.h[i][1] == value: 
                pos = i
                break

        if pos == -1: 
            return

        self.h[pos] = self.h[-1] 
        self.h.pop() 
        heapq.heapify(self.h) 
