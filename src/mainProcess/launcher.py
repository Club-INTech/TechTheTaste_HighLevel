
from email.policy import strict
import sys, os
from hokuyolx import hokuyo
from hokuyolx import lidarstop
from lpastar_pf import LPAStarPathFinder
from Process import CamBotProcess


#path managing
sys.path.insert(1,os.path.join(os.path.dirname(__file__), '..', 'logLib'))

#import part
from logging import log

from multiprocessing import Process, Pipe

class Launcher :
    def __init__(self, version):
        self.version=version

    def processLIDAR(self,conn):
        log.logMessage(2, "start the lidar processus")
        lidar = lidarstop.Lili()
        lidar.lidarstop(conn)

    def processMicro1(self):
        log.logMessage(2, "start the micro1 processus")

    def processMicro2(self):
        log.logMessage(2, "start the micro2 processus")

    def processCamBot(self):
        log.logMessage(2, "start the camBot processus")
        
    def processCamMat(self, parent_CamMat_conn):
        log.logMessage(2, "start the camMat processus")
        camera = CamBotProcess.CamBot()
        Positions = camera.get_positions()
        camera.send_to_lpastar(parent_CamMat_conn, Positions)
        
    def processLpastar(self, child_Lpastar_conn, child_CamMat_conn, child_Micro1_conn):
        log.logMessage(2, "start the lpastar processus")
        lpastar = LPAStarPathFinder()

        goal = child_Lpastar_conn.recv()
        lpastar.find_path(goal, child_Lpastar_conn, child_CamMat_conn, child_Micro1_conn)
        
    
    def config1(self): 
        log.logMessage(2, "start config1")
        parent_LIDAR_conn, child_LIDAR_conn = Pipe()
        parent_CamMat_conn, child_CamMat_conn = Pipe()
        parent_Micro1_conn, child_Micro1_conn = Pipe()
        parent_Lpastar_conn, child_Lpastar_conn = Pipe()
        
        procCamBot = Process(target = self.processCamBot)
        procCamMat = Process(target = self.processCamMat, args = (parent_CamMat_conn,))
        procLIDAR = Process(target = self.processLIDAR, args = (child_LIDAR_conn,))
        procMicro1 = Process(target = self.processMicro1, args = (child_Micro1_conn,))
        procMicro2 = Process(target = self.processMicro2)
        procLpastar = Process(target = self.processLpastar, args = (child_Lpastar_conn, child_CamMat_conn, child_Micro1_conn,))

        processList= [procCamBot, procCamMat, procLIDAR, procMicro1, procMicro2, procLpastar]
        for iter in range(len(processList)) :
            try :
                processList[iter].start()
            except :
                msg=  "process number" + str(iter) + " of the version" + str(self.version) + " failed to launch"
                log.Message(0,msg)
        
        return processList, (parent_LIDAR_conn, child_LIDAR_conn), (parent_CamMat_conn, child_CamMat_conn), (parent_Micro1_conn, child_Micro1_conn), (parent_Lpastar_conn, child_Lpastar_conn)
    
    
    def launch(self):
        log.logMessage(2, "start launching")
        if (self.version == 1):
            return self.config1()
        
            

if __name__ == "__main__" :
    starter = Launcher(1)
    list = starter.launch()
    LIDAR_state, Lpastar_state = 0 , 0
    
    #get the information for lidar to stop the Agent
    parent_LIDAR_conn = list[1][0]
    LIDAR_state = parent_LIDAR_conn.recv() #1 or 0
    
    #send the goal to the lpastarProcess
    parent_Lpastar_conn = list[4][0]
    queue = []
    goal = queue[0]
    parent_Lpastar_conn.send(goal)
    
    #get the information from lpastarProcess to stop the robot
    if parent_Lpastar_conn.recv() == 1 :
        Lpastar_state = 1
    else :
        next_move = parent_Lpastar_conn.recv()
         
     

    
    
    
    
    
    
    
