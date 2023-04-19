import log
from time import sleep
from multiprocessing import Pipe, Process
import logging 

loggerMain = logging.getLogger('Main')
loggerLpa = logging.getLogger('Lpa')
loggerLidar = logging.getLogger('Lidar')
loggerCom1 = logging.getLogger('Com1')
loggerCam1 = logging.getLogger('Cam1')

port1 = "/dev/ttyUSB0"
# port2 = '/dev/ttyUSB1'

# we wait X and Y initialized to start the other process
def isXYinitialised(XYinitialised):
    #while (XYinitialised.value == 0):
    #    log.logMessage(3, "X and Y not initialized", 0)
    #    sleep(1)
    sleep(1)


def startProcess(processCam, listProcess):
    processCam.start()
    #blocking mode function to wait until Xrobot and Yrobot initialised

    for proc in listProcess :
        try :
            proc.start()
        except :
            loggerMain.info( "{} process failed to execute" .format("INFO : mainProcess     :"))

    loggerMain.info( "{} all process started" .format("INFO : mainProcess     :"))
    loggerMain.info("")

def config1(self, processCamMat, processMicro1, processLpastar, processMain, processLIDAR, Xrobot, Yrobot, Hrobot):
        loggerMain.info("Start process : config 1")
        loggerMain.info("")
    
        lidar_main_pipeLidar, lidar_main_pipeMain = Pipe()                  #to kill process
        CamMat_Lpastar_pipeCamMat, CamMat_Lpastar_pipeLpastar = Pipe()      #for obstacles
        lpastar_main_pipeLpastar, lpastar_main_pipeMain = Pipe()            #for goals and path
        main_micro1_pipeMain, main_micro1_pipeMicro1 = Pipe()               #to give order to the micro
        main_micro2_pipeMain, main_micro2_pipeMicro2 = Pipe()


        procCamMat = Process(target = processCamMat, args = (CamMat_Lpastar_pipeCamMat,))
        procLIDAR = Process(target = processLIDAR, args = (lidar_main_pipeLidar,))
        procMicro1 = Process(target = processMicro1, args = (port1, lidar_main_pipeMain, main_micro1_pipeMicro1, Xrobot, Yrobot, Hrobot, 1, 2,))
        # procMicro2 = Process(target = processMicro1, args = (port2, lidar_main_pipeMain, main_micro2_pipeMicro2, Xrobot, Yrobot, Hrobot, 1, 2,))
        procLpastar = Process(target = processLpastar, args = (lpastar_main_pipeLpastar, CamMat_Lpastar_pipeLpastar, Xrobot, Yrobot))
        procMain = Process(target= processMain, args = (main_micro1_pipeMain, main_micro2_pipeMain, lidar_main_pipeMain, lpastar_main_pipeMain, Xrobot, Yrobot) )

        processList= [procLIDAR, procMicro1, procLpastar, procMain]
        # processList= [procMain, procMicro1, procLpastar, procLIDAR]
        startProcess(procCamMat, processList)


        return processList, (lidar_main_pipeLidar, lidar_main_pipeMain), (CamMat_Lpastar_pipeCamMat, CamMat_Lpastar_pipeLpastar), (lpastar_main_pipeLpastar, lpastar_main_pipeMain), (lidar_main_pipeLidar, lidar_main_pipeMain)