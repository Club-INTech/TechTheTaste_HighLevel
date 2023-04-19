import os
import scenario 
from multiprocessing import Pipe, Process

import logging 

loggerMain = logging.getLogger('Main')
loggerLpa = logging.getLogger('Lpa')
loggerLidar = logging.getLogger('Lidar')
loggerCom1 = logging.getLogger('Com1')
loggerCam1 = logging.getLogger('Cam1')


class mainProcess:
    def __init__(self,pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA, pipeLidarToMain):
            self.pipeMainToMicro1 = pipeMainToMicro1
            self.pipeMainToMicro2 = pipeMainToMicro2
            self.pipeMainToLPA = pipeMaintoLPA
            self.pipeLidarToMain = pipeLidarToMain

    def run(self):
        
        #scenario.scenarioSimple(self.pipeMainToMicro1, self.pipeMainToMicro2, self.pipeMainToLPA)
        #scenario.debugLidarProc(self.pipeMainToMicro1, self.pipeMainToMicro2, self.pipeMainToLPA)

        scenario.debugLidar(self, self.pipeMainToMicro1, self.pipeMainToMicro2, self.pipeMainToLPA, self.pipeLidarToMain)
        #scenario.debugRaspy(self.pipeMainToMicro1, self.pipeMainToMicro2, self.pipeMainToLPA)
        
        #scenario.debugSimpleOrderStraight1(self.pipeMainToMicro1, self.pipeMainToMicro2, self.pipeMainToLPA)
        
        #scenario.debugSimpleOrderCaptureCakeMid(self.pipeMainToMicro1, self.pipeMainToMicro2, self.pipeMainToLPA
        #scenario.debugSimpleOrderCaptureCakeRight(self.pipeMainToMicro1, self.pipeMainToMicro2, self.pipeMainToLPA)
        #scenario.debugSimpleOrderCaptureCakeLeft(self.pipeMainToMicro1, self.pipeMainToMicro2, self.pipeMainToLPA)
        
        #scenario.scenarioApproval(self.pipeMainToMicro1, self.pipeMainToMicro2, self.pipeMainToLPA)
        #scenario.scenarioGreenStartPushingCake(self.pipeMainToMicro1, self.pipeMainToMicro2, self.pipeMainToLPA)
        #scenario.scenarioBlueStartPushingCake(self.pipeMainToMicro1, self.pipeMainToMicro2, self.pipeMainToLPA)
        
        
        

