import sys, os
import scenario 
from multiprocessing import Pipe, Process


class mainProcess:
    def __init__(self,pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA, pipeLidarToMain):
            self.pipeMainToMicro1 = pipeMainToMicro1
            self.pipeMainToMicro2 = pipeMainToMicro2
            self.pipeMainToLPA = pipeMaintoLPA
            self.pipeLidarToMain = pipeLidarToMain


    def run(self):
        #scenario.scenarioSimple(self.pipeMainToMicro1, self.pipeMainToMicro2, self.pipeMainToLPA)
        #scenario.debugLidarProc(self.pipeMainToMicro1, self.pipeMainToMicro2, self.pipeMainToLPA)
        #scenario.debugLidar(self.pipeMainToMicro1, self.pipeMainToMicro2, self.pipeMainToLPA, self.pipeLidarToMain)
        #scenario.debugRaspy(self.pipeMainToMicro1, self.pipeMainToMicro2, self.pipeMainToLPA)
        scenario.debugSimpleOrder(self.pipeMainToMicro1, self.pipeMainToMicro2, self.pipeMainToLPA)

