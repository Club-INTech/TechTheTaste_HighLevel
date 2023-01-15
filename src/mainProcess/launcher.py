
from email.policy import strict
import sys, os
import mainProcess
#from hokuyolx import hokuyo
import time
import random
#from Process import CamBotProcess


#path managing
sys.path.insert(1,os.path.join(os.path.dirname(__file__), '..', 'utils'))
sys.path.insert(1,os.path.join(os.path.dirname(__file__), '..', 'lpastarProcess'))

#import part
import log
from LPAStarPathFinder import LPAStarPathFinder
from processManager import config1
#from lidarProcess import lidarstop


from multiprocessing import Process, Pipe, Value


#global variable 
Xrobot = Value('i', 0) #position X of the robot should not be over 12 000 ticks
Yrobot = Value('i', 0) #position Y of the robot should not be over 12 000 ticks
XYinitialised = Value('i', 0) # to know if Xrobot and Yrobothave been initialised by the cam process, 0 = flase, 1 = True

class Launcher :
    def __init__(self, version):
        self.version=version

    def processMain(self, pipeMicro1, pipeMicro2, lidar_main_pipeMain, lpastar_main_pipMain, Xrobot, Yrobot):
        log.logMessage(2, "start the main processus")
        mainProcss = mainProcess.mainProcess(pipeMicro1, pipeMicro2, lpastar_main_pipMain)
        mainProcss.run()

    def processLIDAR(self,lidar_main_pipeLidar):
        log.logMessage(2, "start the lidar processus")
        #lidar = lidarProcess.lidarstop()
        #lidar.lidarstop(lidar_main_pipeLidar)
        
    def processMicro1(self):
        log.logMessage(2, "start the micro1 processus")

    def processMicro2(self):
        log.logMessage(2, "start the micro2 processus")

    def processCamBot(self):
        log.logMessage(2, "start the camBot processus")
        
    def processCamMat(self, CamMat_Lpastar_pipeCamMat):
        log.logMessage(2, "start the camMat processus")
        
        def generate_obstacles() :
            obstacles = [(0.0, 1000.0, 24.0),
                    (1500.0, 0.0, 24.0),
                    (3000.0, 1000.0, 24.0),
                    (0.0, 2000.0, 24.0)]
            random.seed(time.time())
            for i in range(100):
                x = random.uniform(0.0, 3000.0)
                y = random.uniform(0.0, 2000.0)
                w = 50.0 * random.random()
                obstacles.append((x, y, w))
            return obstacles
        
        while True :
            if CamMat_Lpastar_pipeCamMat.poll():
                if CamMat_Lpastar_pipeCamMat.recv() == 4 :
                    obstacles = generate_obstacles()
                    CamMat_Lpastar_pipeCamMat.send(obstacles)
        
        
    def processLpastar(self, lpastar_main_pipeLpastar, CamMat_Lpastar_pipeLpastar, Xrobot, Yrobot):
        log.logMessage(2, "start the lpastar processus")
        lpastar = LPAStarPathFinder()
        
        while True :
            if lpastar_main_pipeLpastar.poll():
                goal = lpastar_main_pipeLpastar.recv()
                X = Xrobot.value
                Y = Yrobot.value
                lpastar.find_path(goal[1], CamMat_Lpastar_pipeLpastar, lpastar_main_pipeLpastar, X, Y) #lpastarProcess needs CamBotProcess and MainProcess
                
    
    
    def launch(self):
        log.logMessage(2, "start launching")
        if (self.version == 1):
            return config1(self, self.processCamBot, self.processCamMat, self.processMicro1, self.processMicro2, self.processLpastar, self.processMain, Xrobot, Yrobot, XYinitialised)
        
            
if __name__ == "__main__" :
    starter = Launcher(1)
    list = starter.launch()

    
    
         
     

    
    
    
    
    
    
    