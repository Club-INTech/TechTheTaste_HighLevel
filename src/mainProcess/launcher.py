from email.policy import strict
import sys, os
import mainProcess
import time
import random
import logging


#path managing
sys.path.insert(1,os.path.join(os.path.dirname(__file__), '..', 'utils'))
sys.path.insert(1,os.path.join(os.path.dirname(__file__), '..', 'lpastarProcess'))
sys.path.insert(1,os.path.join(os.path.dirname(__file__), '..', 'CamProcess'))
sys.path.insert(1,os.path.join(os.path.dirname(__file__), '..', 'lidarProcess'))
sys.path.insert(1,os.path.join(os.path.dirname(__file__), '..', 'microProcess'))

#import part
import log
from lpastarProcess.LPAStarPathFinder import LPAStarPathFinder
from processManager import config1
from com import RxPipe
from testing import generate_obstacles
from micro_process import MicroProcess
import lidarProcess 

from multiprocessing import Process, Pipe, Value, current_process

#global variable 
Xrobot = Value('f', 0) #meter
Yrobot = Value('f', 0) #meter
Hrobot = Value('f', 0) #meter (head)
Xarm = Value('f', 0) 
Yarm = Value('f', 0)
XYinitialised = Value('i', 0) # to know if Xrobot and Yrobothave been initialised by the cam process, 0 = false, 1 = True
# TODO, add Hrobot to config 1
# fix the issue about Lpastar integer and float


def createLog(name, filepath, loggingLevel):
    logger = logging.getLogger(name)
    logger.setLevel(loggingLevel)
    handler = logging.FileHandler(filepath)
    handler.setFormatter( logging.Formatter('%(message)s') )
    logger.addHandler(handler)
    logger.addHandler(logging.StreamHandler())
    logger.info('')
    logger.info('---------------------------------------------------------------------------------')
    logger.info('init logging for ' + name + ' done')
    logger.info('---------------------------------------------------------------------------------')
    logger.info('')
    handler.setFormatter( logging.Formatter('%(asctime)s - %(levelname)s - %(message)s') )
    return logger

class Launcher :
    def __init__(self, version):
        self.version=version
        #initLogin
        self.loggerMain = createLog('Main', 'log/main.txt', logging.INFO)
        self.loggerLpa = createLog('Lpa', 'log/lpa.txt', logging.INFO)
        self.loggerLidar = createLog('Lidar', 'log/lidar.txt', logging.INFO)
        self.loggerCom1 = createLog('Com1', 'log/com1.txt', logging.INFO)
        self.loggerCam1 = createLog('Cam1', 'log/cam1.txt', logging.INFO)
        

    def processMain(self, pipeMicro1, pipeMicro2, lidar_main_pipeMain, lpastar_main_pipMain, Xrobot, Yrobot):
        mainProcss = mainProcess.mainProcess(pipeMicro1, pipeMicro2, lpastar_main_pipMain, lidar_main_pipeMain)
        mainProcss.run()
        

    def processLIDAR(self,lidar_main_pipeLidar):
        self.loggerLidar.info("INFO : lidarProcess    : starting the process")
        lidar=lidarProcess.Lili()
        lidar.lidarstop(lidar_main_pipeLidar)
        

    def processMicro1(self, port, pipeLiDAR, pipeMain, robot_x, robot_y, robot_heading, axle_track, logg):
        self.loggerCom1.info("INFO : microProcess    : starting the process")      
        microProcss = MicroProcess(port, pipeLiDAR, pipeMain, robot_x, robot_y, robot_heading, axle_track,logg)
        microProcss.run()
        

    def processCamMat(self, CamMat_Lpastar_pipeCamMat):
        self.loggerCam1.info("INFO : CamMatProcess   : not started")
        #obstacles = generate_obstacles()
        #while True :
        #    if CamMat_Lpastar_pipeCamMat.poll():
        #        if CamMat_Lpastar_pipeCamMat.recv() == 0 :
        #            CamMat_Lpastar_pipeCamMat.send(obstacles)
        #            #RxPipe(CamMat_Lpastar_pipeCamMat)
        
        
    def processLpastar(self, lpastar_main_pipeLpastar, CamMat_Lpastar_pipeLpastar, Xrobot, Yrobot):
        self.loggerLpa.info("INFO : lpastarProcess  : not started")
        
        #lpastar = LPAStarPathFinder()
        #
        #while True :
        #    if lpastar_main_pipeLpastar.poll():
        #        goal = lpastar_main_pipeLpastar.recv()
        #        X = Xrobot.value
        #        Y = Yrobot.value
        #        lpastar.find_path(goal[1], CamMat_Lpastar_pipeLpastar, lpastar_main_pipeLpastar, X, Y) #lpastarProcess needs CamBotProcess and MainProcess
                
    
    def launch(self):
        if (self.version == 1):
            return config1(self, self.processCamMat, self.processMicro1, self.processLpastar, self.processMain, self.processLIDAR, Xrobot, Yrobot, Hrobot)
        



if __name__ == "__main__" :
    starter = Launcher(1)
    list = starter.launch()

    
    
         
     

    
    
    
    
    
    
    