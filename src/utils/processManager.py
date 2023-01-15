import log
from time import sleep
from multiprocessing import Pipe, Process

# we wait X and Y initialized to start the other process
def isXYinitialised(XYinitialised):
    #while (XYinitialised.value == 0):
    #    log.logMessage(3, "X and Y not initialized")
    #    sleep(1)
    sleep(1)



def startProcess(processCam, listProcess, boolXY):
    processCam.start()
    #blocking mode function to wait until Xrobot and Yrobot initialised
    isXYinitialised(boolXY)

    for proc in listProcess :
        try :
            proc.start()
        except :
            log.logMessage(0, "process failed to execute")

    log.logMessage(1, "all process started!")

def config1(self,processCamBot, processCamMat, processMicro1, processMicro2, processLpastar, processMain, Xrobot, Yrobot, XYinitialised): 
        log.logMessage(2, "start config1")
        lidar_main_pipeLidar, lidar_main_pipeMain = Pipe()                  #to kill process
        CamMat_Lpastar_pipeCamMat, CamMat_Lpastar_pipeLpastar = Pipe()      #for obstacles
        lpastar_main_pipeLpastar, lpastar_main_pipeMain = Pipe()            #for goals and path
        
        #a pipe has the nomenclature parent_child_pipe(Parent or Child)
        main_micro1_pipeMain, main_micro1_pipeMicro1 = Pipe()
        main_micro2_pipeMain, main_micro2_pipeMicro2 = Pipe()


        procCamBot = Process(target = processCamBot)
        procCamMat = Process(target = processCamMat, args = (CamMat_Lpastar_pipeCamMat,))
        #procLIDAR = Process(target = self.processLIDAR, args = (lidar_main_pipeLidar,))
        procMicro1 = Process(target = processMicro1, args = ())
        procMicro2 = Process(target = processMicro2)
        procLpastar = Process(target = processLpastar, args = (lpastar_main_pipeLpastar, CamMat_Lpastar_pipeLpastar, Xrobot, Yrobot))
        procMain = Process(target= processMain, args = (main_micro1_pipeMain, main_micro2_pipeMain, lidar_main_pipeMain, lpastar_main_pipeMain, Xrobot, Yrobot) )

        #processList= [procMain, procCamBot, procCamMat, procLIDAR, procMicro1, procMicro2, procLpastar]
        processList= [procMain, procCamBot, procMicro1, procMicro2, procLpastar]
        startProcess(procCamMat, processList, XYinitialised)


        return processList, (lidar_main_pipeLidar, lidar_main_pipeMain), (CamMat_Lpastar_pipeCamMat, CamMat_Lpastar_pipeLpastar), (lpastar_main_pipeLpastar, lpastar_main_pipeMain)