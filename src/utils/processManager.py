import log
from time import sleep

# we wait X and Y initialized to start the other process
def isXYinitialised(XYinitialised):
    while (XYinitialised.value == 0):
        log.logMessage(3, "X and Y not initialized")
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
