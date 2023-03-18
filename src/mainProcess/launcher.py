
from email.policy import strict
import sys, os
import mainProcess
from hokuyolx import hokuyo
import time
import random
import logging


#path managing
sys.path.insert(1,os.path.join(os.path.dirname(__file__), '..', 'utils'))
sys.path.insert(1,os.path.join(os.path.dirname(__file__), '..', 'lpastarProcess'))
sys.path.insert(1,os.path.join(os.path.dirname(__file__), '..', 'CamProcess'))
sys.path.insert(1,os.path.join(os.path.dirname(__file__), '..', 'lidarProcess'))

#import part
import log
from lpastarProcess.LPAStarPathFinder import LPAStarPathFinder
from processManager import config1
from com import RxPipe
from testing import generate_obstacles
# TODO change lidar on lidarProcess import lidarProcess 

from multiprocessing import Process, Pipe, Value, current_process

#global variable 
Xrobot = Value('i', 0) #position X of the robot should not be over 12 000 ticks
Yrobot = Value('i', 0) #position Y of the robot should not be over 12 000 ticks
XYinitialised = Value('i', 0) # to know if Xrobot and Yrobothave been initialised by the cam process, 0 = false, 1 = True

def createLog(name, filepath, loggingLevel):
    logger = logging.getLogger(name)
    logger.setLevel(loggingLevel)
    handler = logging.FileHandler(filepath)
    handler.setFormatter( logging.Formatter('%(message)s') )
    logger.addHandler(handler)
    logger.addHandler(logging.StreamHandler())
    logger.info('')
    logger.info('')
    logger.info('')
    logger.info('---------------------------------------------------------------------------------')
    logger.info('init logging for ' + name + ' done')
    logger.info('---------------------------------------------------------------------------------')
    handler.setFormatter( logging.Formatter('%(asctime)s - %(levelname)s - %(message)s') )
    logger.info("just test :)")
    return logger

class Launcher :
    def __init__(self, version):
        self.version=version
        #initLogin
        self.loggerMain = createLog('Main', 'log/main.txt', logging.INFO)
        self.loggerLpa = createLog('Lpa', 'log/lpa.txt', logging.INFO)
        self.loggerLidar = createLog('Lidar', 'log/lidar.txt', logging.INFO)
        self.loggerCom2 = createLog('Com2', 'log/com2.txt', logging.INFO)
        self.loggerCom1 = createLog('Com1', 'log/com1.txt', logging.INFO)

    def processMain(self, pipeMicro1, pipeMicro2, lidar_main_pipeMain, lpastar_main_pipMain, Xrobot, Yrobot):
        log.logMessage(2, "start the main processus", 0)
        mainProcss = mainProcess.mainProcess(pipeMicro1, pipeMicro2, lpastar_main_pipMain, lidar_main_pipeMain)
        mainProcss.run()

    # TODO, removre the comment
    #def processLIDAR(self,lidar_main_pipeLidar):
    #    log.logMessage(2, "start the lidar processus", 1)
    #    lidar=lidarProcess.Lili()
    #    lidar.lidarstop(lidar_main_pipeLidar)
        
    def processMicro1(self):
        log.logMessage(2, "start the micro1 processus", 2)

    def processMicro2(self):
        log.logMessage(2, "start the micro2 processus", 3)

    def processCamBot(self):
        log.logMessage(2, "start the camBot processus", 4)
        
    def processCamMat(self, CamMat_Lpastar_pipeCamMat):
        log.logMessage(2, "start the camMat processus", 5)
        
        while True :
            if CamMat_Lpastar_pipeCamMat.poll():
                if CamMat_Lpastar_pipeCamMat.recv() == 0 :
                    obstacles = generate_obstacles()
                    CamMat_Lpastar_pipeCamMat.send(obstacles)
                    #RxPipe(CamMat_Lpastar_pipeCamMat)
        
        
    def processLpastar(self, lpastar_main_pipeLpastar, CamMat_Lpastar_pipeLpastar, Xrobot, Yrobot):
        log.logMessage(2, "start the lpastar processus", 6)
        lpastar = LPAStarPathFinder()
        
        while True :
            if lpastar_main_pipeLpastar.poll():
                goal = lpastar_main_pipeLpastar.recv()
                X = Xrobot.value
                Y = Yrobot.value
                lpastar.find_path(goal[1], CamMat_Lpastar_pipeLpastar, lpastar_main_pipeLpastar, X, Y) #lpastarProcess needs CamBotProcess and MainProcess
                
    
    
    def launch(self):
        log.logMessage(2, "start launching", 7)
        if (self.version == 1):
            return config1(self, self.processCamBot, self.processCamMat, self.processMicro1, self.processMicro2, self.processLpastar, self.processMain, self.processLIDAR, Xrobot, Yrobot, XYinitialised)
        



if __name__ == "__main__" :
    starter = Launcher(1)
    # TODO, repair LiDAR process
    # list = starter.launch()

    
    
         
     

    
    
    
    
    
    
    