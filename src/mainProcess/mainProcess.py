import sys, os
import scenario 
from multiprocessing import Pipe, Process


class mainProcess:
    def __init__(self,pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA):
            self.pipeMainToMicro1 = pipeMainToMicro1
            self.pipeMainToMicro2 = pipeMainToMicro2
            self.pipeMainToLPA = pipeMaintoLPA


    def run(self):
        #scenario.scenarioSimple(self.pipeMainToMicro1, self.pipeMainToMicro2, self.pipeMainToLPA)
        scenario.debugLidarProc(self.pipeMainToMicro1, self.pipeMainToMicro2, self.pipeMainToLPA)


