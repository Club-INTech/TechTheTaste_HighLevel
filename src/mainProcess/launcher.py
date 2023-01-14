
from email.policy import strict
import sys, os
import mainProcess
from hokuyolx import hokuyo
import time
import random
#from hokuyolx import lidarstop
#from Process import CamBotProcess


#path managing
sys.path.insert(1,os.path.join(os.path.dirname(__file__), '..', 'utils'))
sys.path.insert(1,os.path.join(os.path.dirname(__file__), '..', 'lpastarProcess'))

#import part
import log
from LPAStarPathFinder import LPAStarPathFinder
from processManager import startProcess


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

    #def processLIDAR(self,lidar_main_pipeLidar):
    #    log.logMessage(2, "start the lidar processus")
    #    lidar = lidarstop.Lili()
    #    lidar.lidarstop(lidar_main_pipeLidar)
        

    def processMicro1(self, micro1_lpastar_pipeMicro1):
        log.logMessage(2, "start the micro1 processus")
        
        position = (0,0,10)
        
        while True :
            if micro1_lpastar_pipeMicro1.poll():
                order = micro1_lpastar_pipeMicro1.recv()
                if order == 2 :
                    micro1_lpastar_pipeMicro1.send(position)
    

    def processMicro2(self):
        log.logMessage(2, "start the micro2 processus")

    def processCamBot(self):
        log.logMessage(2, "start the camBot processus")
        
    def processCamMat(self, CamMat_Lpastar_pipeCamMat):
        log.logMessage(2, "start the camMat processus")
        #camera = CamBotProcess.CamBot()
        #Positions = camera.get_positions()                          
        #camera.send_to_lpastar(CamMat_Lpastar_pipeCamMat, Positions)       #send obstacles or lpastarProcess
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
        
        
    def processLpastar(self, lpastar_main_pipeLpastar, CamMat_Lpastar_pipeLpastar, micro1_lpastar_pipeLpastar, Xrobot, Yrobot):
        log.logMessage(2, "start the lpastar processus")
        lpastar = LPAStarPathFinder()
        
        while True :
            if lpastar_main_pipeLpastar.poll():
                goal = lpastar_main_pipeLpastar.recv()
                X = Xrobot.value
                Y = Yrobot.value
                lpastar.find_path(goal[1], CamMat_Lpastar_pipeLpastar, lpastar_main_pipeLpastar, X, Y) #lpastarProcess needs CamBotProcess and MainProcess
                
                
    def config1(self): 
        log.logMessage(2, "start config1")
        lidar_main_pipeLidar, lidar_main_pipeMain = Pipe()                  #to kill process
        CamMat_Lpastar_pipeCamMat, CamMat_Lpastar_pipeLpastar = Pipe()      #for obstacles
        lpastar_main_pipeLpastar, lpastar_main_pipeMain = Pipe()            #for goals and path
        micro1_lpastar_pipeMicro1, micro1_lpastar_pipeLpastar = Pipe()      #for current position
        
        #a pipe has the nomenclature parent_child_pipe(Parent or Child)
        main_micro1_pipeMain, main_micro1_pipeMicro1 = Pipe()
        main_micro2_pipeMain, main_micro2_pipeMicro2 = Pipe()


        procCamBot = Process(target = self.processCamBot)
        procCamMat = Process(target = self.processCamMat, args = (CamMat_Lpastar_pipeCamMat,))
        #procLIDAR = Process(target = self.processLIDAR, args = (lidar_main_pipeLidar,))
        procMicro1 = Process(target = self.processMicro1, args = (micro1_lpastar_pipeMicro1,))
        procMicro2 = Process(target = self.processMicro2)
        procLpastar = Process(target = self.processLpastar, args = (lpastar_main_pipeLpastar, CamMat_Lpastar_pipeLpastar, micro1_lpastar_pipeLpastar,Xrobot, Yrobot))
        procMain = Process(target= self.processMain, args = (main_micro1_pipeMain, main_micro2_pipeMain, lidar_main_pipeMain, lpastar_main_pipeMain, Xrobot, Yrobot) )

        #processList= [procMain, procCamBot, procCamMat, procLIDAR, procMicro1, procMicro2, procLpastar]
        processList= [procMain, procCamBot, procMicro1, procMicro2, procLpastar]
        startProcess(procCamMat, processList, XYinitialised)


        return processList, (lidar_main_pipeLidar, lidar_main_pipeMain), (CamMat_Lpastar_pipeCamMat, CamMat_Lpastar_pipeLpastar), (micro1_lpastar_pipeMicro1, micro1_lpastar_pipeLpastar), (lpastar_main_pipeLpastar, lpastar_main_pipeMain)
    
    
    def launch(self):
        log.logMessage(2, "start launching")
        if (self.version == 1):
            return self.config1()
        
            

if __name__ == "__main__" :
    starter = Launcher(1)
    list = starter.launch()
    
    #lidar_main_pipeLidar, lidar_main_pipeMain = list[1][0],list[1][1]              
    #CamMat_Lpastar_pipeCamMat, CamMat_Lpastar_pipeLpastar = list[2][0],list[2][1]     
    #lpastar_main_pipeLpastar, lpastar_main_pipeMain = list[3][0],list[3][1]     
    #micro1_lpastar_pipeMicro1, micro1_lpastar_pipeLpastar = list[4][0],list[4][1]
    
    #test CamBot to lpastar for obtstacles
    #parent_CamMat_conn.send(1) #in proCamMat
    #print("lpastar reçoit dans le child_CamMat_conn : " + child_CamMat_conn.recv()) #in procLpastar
    
    #test Lidar to MainProcess for stop
    #parent_LIDAR_conn.send(2) #in proLIDAR
    #print("MainProcess reçoit dans le child_LIDAR_conn : " + child_LIDAR_conn.recv()) #in procMain
    
    #test lpastar to MainProcess for path
    #parent_Lpastar_conn.send(3) #in procLpastar
    #print("MainProcess reçoit dans le child_Lpastar_conn : " + child_Lpastar_conn.recv()) #in MainProcess
    
    #test MainProcess to lpastar for goal
    #child_Lpastar_conn.send(4) #in procMain
    #print("lpastar reçoit dans le parent_Lpastar_conn : " + parent_Lpastar_conn.recv()) #in procLpastar
    
    #test Micro1 to lpastar for current position
    #child_Lpastar_conn.send(4) #in procMain
    #print("lpastar reçoit dans le parent_Lpastar_conn : " + parent_Lpastar_conn.recv()) #in procLpastar
    
    
         
     

    
    
    
    
    
    
    