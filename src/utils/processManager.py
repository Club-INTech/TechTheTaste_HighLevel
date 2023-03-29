import log
from time import sleep
from multiprocessing import Pipe, Process

port = "/dev/serial/usb-devices"


# we wait X and Y initialized to start the other process
def isXYinitialised(XYinitialised):
    #while (XYinitialised.value == 0):
    #    log.logMessage(3, "X and Y not initialized", 0)
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
            log.logMessage(0, "process failed to execute",0)

    log.logMessage(1, "all process started!",0)

def config1(self, processCamMat, processMicro1, processLpastar, processMain, processLIDAR, Xrobot, Yrobot, XYinitialised): 
        log.logMessage(2, "start config1",0)
        lidar_main_pipeLidar, lidar_main_pipeMain = Pipe()                  #to kill process
        CamMat_Lpastar_pipeCamMat, CamMat_Lpastar_pipeLpastar = Pipe()      #for obstacles
        lpastar_main_pipeLpastar, lpastar_main_pipeMain = Pipe()            #for goals and path
        main_micro1_pipeMain, main_micro1_pipeMicro1 = Pipe()               #to give order to the micro
        main_micro2_pipeMain, main_micro2_pipeMicro2 = Pipe()


        procCamMat = Process(target = processCamMat, args = (CamMat_Lpastar_pipeCamMat,))
        procLIDAR = Process(target = processLIDAR, args = (lidar_main_pipeLidar,))
        procMicro1 = Process(target = processMicro1, args = (port, lidar_main_pipeMain, main_micro1_pipeMicro1, Xrobot, Yrobot, 0, 1, 1,))
        procLpastar = Process(target = processLpastar, args = (lpastar_main_pipeLpastar, CamMat_Lpastar_pipeLpastar, Xrobot, Yrobot))
        procMain = Process(target= processMain, args = (main_micro1_pipeMain, main_micro2_pipeMain, lidar_main_pipeMain, lpastar_main_pipeMain, Xrobot, Yrobot) )

        #processList= [procMain, procCamBot, procCamMat, procLIDAR, procMicro1, procMicro2, procLpastar]
        processList= [procMain, procMicro1, procLpastar, procLIDAR]
        startProcess(procCamMat, processList, XYinitialised)


        return processList, (lidar_main_pipeLidar, lidar_main_pipeMain), (CamMat_Lpastar_pipeCamMat, CamMat_Lpastar_pipeLpastar), (lpastar_main_pipeLpastar, lpastar_main_pipeMain), (lidar_main_pipeLidar, lidar_main_pipeMain)