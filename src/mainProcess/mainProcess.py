import sys, os
import scenario 
from multiprocessing import Pipe, Process


class mainProcess:
    def __init__(self,pipeMainToMicro1, pipeMainToMicro2):
            self.pipeMainToMicro1 = pipeMainToMicro1
            self.pipeMainToMicro2 = pipeMainToMicro2


    def run(self):
        scenario.scenarioSimple(self.pipeMainToMicro1, self.pipeMainToMicro2)