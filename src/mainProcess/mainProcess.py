import os
import scenario 
from multiprocessing import Pipe, Process


class mainProcess:
    def __init__(self, pipeMainToActua, pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA, pipeLidarToMain):
            self.pipeMainToMicro1 = pipeMainToMicro1
            self.pipeMainToMicro2 = pipeMainToMicro2
            self.pipeMainToLPA = pipeMaintoLPA
            self.pipeLidarToMain = pipeLidarToMain
            self.pipeMainToActua = pipeMainToActua

    def run(self):
        #scenario.scenarioSimple(self.pipeMainToMicro1, self.pipeMainToMicro2, self.pipeMainToLPA)
        #scenario.debugLidarProc(self.pipeMainToMicro1, self.pipeMainToMicro2, self.pipeMainToLPA)
        #scenario.debugLidar(self.pipeMainToMicro1, self.pipeMainToMicro2, self.pipeMainToLPA, self.pipeLidarToMain)
        #scenario.debugLidar(self.pipeMainToMicro1, self.pipeMainToMicro2, self.pipeMainToLPA, self.pipeLidarToMain)
        #scenario.debugRaspy(self.pipeMainToMicro1, self.pipeMainToMicro2, self.pipeMainToLPA)
        #scenario.debugActioneur2A(self.pipeMainToMicro1, self.pipeMainToMicro2, self.pipeMainToLPA, self.pipeMainToActua)
        scenario.homolog2A(self.pipeMainToMicro1, self.pipeMainToMicro2, self.pipeMainToLPA, self.pipeMainToActua)

        #scenario.debugSimpleOrderStraight1(self.pipeMainToMicro1, self.pipeMainToMicro2, self.pipeMainToLPA, self.pipeMainToActua)
        #scenario.debugSimpleOrderStraight2(self.pipeMainToMicro1, self.pipeMainToMicro2, self.pipeMainToLPA, self.pipeMainToActua)
        #scenario.debugSimpleOrderStraight3(self.pipeMainToMicro1, self.pipeMainToMicro2, self.pipeMainToLPA)
        #scenario.debugSimpleOrderStraight4(self.pipeMainToMicro1, self.pipeMainToMicro2, self.pipeMainToLPA)

        #scenario.debugSimpleOrderDiagonal(self.pipeMainToMicro1, self.pipeMainToMicro2, self.pipeMainToLPA)
        
        #scenario.debugSimpleOrderTurn(self.pipeMainToMicro1, self.pipeMainToMicro2, self.pipeMainToLPA)
        
        #scenario.debugSimpleOrderCaptureCakeMid(self.pipeMainToMicro1, self.pipeMainToMicro2, self.pipeMainToLPA
        #scenario.debugSimpleOrderCaptureCakeRight(self.pipeMainToMicro1, self.pipeMainToMicro2, self.pipeMainToLPA)
        #scenario.debugSimpleOrderCaptureCakeLeft(self.pipeMainToMicro1, self.pipeMainToMicro2, self.pipeMainToLPA)

