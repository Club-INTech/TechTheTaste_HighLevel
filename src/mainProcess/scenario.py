# one function represents one scenario of the robot
# please, give clear name to the scenario so we they could be as useful as possible
import time
import orderInterProcess as ord
import sys, os
from multiprocessing import Pipe, Process
#path managing
sys.path.insert(1,os.path.join(os.path.dirname(__file__), '..', 'utils'))
sys.path.insert(1,os.path.join(os.path.dirname(__file__), '..'))
from microProcess.constants import *

#import part
import log
import math
import logging 

loggerMain = logging.getLogger('Main')
loggerLpa = logging.getLogger('Lpa')
loggerLidar = logging.getLogger('Lidar')
loggerCom1 = logging.getLogger('Com1')
loggerCam1 = logging.getLogger('Cam1')

#-----------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------ debug part -----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------

def debugLPA(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA):
    log.logMessage(2,"scenario debug of LPA*", 0)
    
    OrderManager = ord.OrderToMicroProcress(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA)
    
    log.logMessage(1, "orderManager created", 0)

    OrderManager.askLPAprocess(1000, 1000)

    log.logMessage(2, "asked for a small moov", 0) 

    OrderManager.askLPAprocess(1999, 2999)

    log.logMessage(2, "asked for a big moov", 0) 

    time.sleep(2)

    log.logMessage(2,"simulation finished", 0)
    
def debugLidar(self, pipeMainToMicro1, pipeMainToMicro2, pipeMainToLPA, pipeLidarToMain):
    loggerMain.info( "{} scenario debug lidar" .format("INFO : mainProcess     :"))
    loggerMain.info("")
    while True :
        if pipeLidarToMain.poll():
            status = pipeLidarToMain.recv()
            print(status)
            
    
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------ test movement --------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------

    
def debugSimpleOrderStraight1(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA):
    log.logMessage(2,"scenario test simple order : Straight (1,0)", 0)
    
    OrderManager = ord.OrderToMicroProcress(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA)
   
    OrderManager.moovToSimple(0.5,0)
    
    log.logMessage(2,"simulation finished", 0)
    
    
def debugSimpleOrderCaptureCakeMid(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA):
    log.logMessage(2,"scenario test simple order : CaptureCake (1,1)", 0)
    
    OrderManager = ord.OrderToMicroProcress(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA)
    
    RIGHT, MID, LEFT = 1,2,3
    x, y = 0.2, 0
    slot = MID
    OrderManager.captureCake(x, y, slot)
    
    log.logMessage(2,"simulation finished", 0)
    
def debugSimpleOrderCaptureCakeRight(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA):
    log.logMessage(2,"scenario test simple order : CaptureCake (1,1)", 0)
    
    OrderManager = ord.OrderToMicroProcress(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA)
    
    RIGHT, MID, LEFT = 1,2,3
    x, y = 0.2, 0
    slot = RIGHT
    OrderManager.captureCake(x, y, slot)
    
    log.logMessage(2,"simulation finished", 0)

def debugSimpleOrderCaptureCakeLeft(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA):
    log.logMessage(2,"scenario test simple order : CaptureCake (1,1)", 0)
    
    OrderManager = ord.OrderToMicroProcress(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA)
    
    RIGHT, MID, LEFT = 1,2,3
    x, y = 0.2, 0
    slot = LEFT
    OrderManager.captureCake(x, y, slot)
    
    log.logMessage(2,"simulation finished", 0)
    

#-----------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------ scenario part --------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------

def scenarioSimpleGreen(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA):
    log.logMessage(2,"scenario simple", 0)
    
    OrderManager = ord.OrderToMicroProcress(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA)
    
    positionGlacage1, positionCreme1, positionGenoise1 = (0,0), (0,0), (0,0)
    positionGlacage2, positionCreme2, positionGenoise2 = (0,0), (0,0), (0,0)
    positionDeposit1, positionDeposit2 = (0,0), (0,0)
    positionEnd = (0,0)
    
    RIGHT, MIDDLE, LEFT = 1, 2, 3
    
    ########## First wave ############
    
    OrderManager.openCake(LEFT)
    OrderManager.openCake(MIDDLE)
    OrderManager.openCake(RIGHT)
   
    OrderManager.moovToSimple(positionGlacage1)
    OrderManager.captureCake(positionGlacage1,MIDDLE)
    OrderManager.lockCake(MIDDLE)
    
    OrderManager.moovToSimple(positionCreme1)
    OrderManager.captureCake(positionCreme1,LEFT)
    OrderManager.lockCake(LEFT)
    
    OrderManager.moovToSimple(positionGenoise1)
    OrderManager.captureCake(positionGenoise1,RIGHT)
    OrderManager.lockCake(RIGHT)
    
    #Phase 1
    
    OrderManager.moovToSimple(positionDeposit1)
    
    OrderManager.sortCakePhase1(genoise=RIGHT,creme=LEFT,glacage=MIDDLE)
    
    OrderManager.putCherry()
    OrderManager.openCake(RIGHT)
    OrderManager.releaseCake()
    
    #Phase 2
    
    OrderManager.moovToSimple(positionDeposit1) #a bit different
    
    OrderManager.sortCakePhase2(genoise=RIGHT,creme=LEFT,glacage=MIDDLE)
    
    OrderManager.putCherry()
    OrderManager.openCake(RIGHT)
    OrderManager.releaseCake()
    
    #Phase 3
    
    OrderManager.moovToSimple(positionDeposit1) #a bit different
    
    OrderManager.sortCakePhase3(genoise=RIGHT,creme=LEFT,glacage=MIDDLE)
    
    OrderManager.putCherry()
    OrderManager.openCake(RIGHT)
    OrderManager.releaseCake()
    
    ########## Second wave ############
    
    OrderManager.openCake(LEFT)
    OrderManager.openCake(MIDDLE)
    OrderManager.openCake(RIGHT)
    
    OrderManager.moovToSimple(positionGenoise2)
    OrderManager.captureCake(positionGenoise2,RIGHT)
    OrderManager.lockCake(RIGHT)
    
    OrderManager.moovToSimple(positionCreme2)
    OrderManager.captureCake(positionCreme2,LEFT)
    OrderManager.lockCake(LEFT)
    
    OrderManager.moovToSimple(positionGlacage2)
    OrderManager.captureCake(positionGlacage2, MIDDLE)
    OrderManager.lockCake(MIDDLE)
    
    #Phase 1
    
    OrderManager.moovToSimple(positionDeposit2)
    
    OrderManager.sortCakePhase1(genoise=RIGHT,creme=LEFT,glacage=MIDDLE)
    OrderManager.putCherry()
    OrderManager.openCake(RIGHT)
    OrderManager.releaseCake()
    
    #Phase 2
    
    OrderManager.moovToSimple(positionDeposit2) #a bit different
    
    OrderManager.sortCakePhase2(genoise=RIGHT,creme=LEFT,glacage=MIDDLE)
    
    OrderManager.putCherry()
    OrderManager.openCake(RIGHT)
    OrderManager.releaseCake()
    
    #Phase 3
    
    OrderManager.moovToSimple(positionDeposit2) #a bit different
    
    OrderManager.sortCakePhase3(genoise=RIGHT,creme=LEFT,glacage=MIDDLE)
    
    OrderManager.putCherry()
    OrderManager.openCake(RIGHT)
    OrderManager.releaseCake()
    
    OrderManager.moovToSimple(positionEnd)
    
    log.logMessage(2,"simulation finished", 0)
    
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------ DavinciBot --------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------

def scenarioApproval(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA):
    
    log.logMessage(2,"scenario approval ", 0)
    
    OrderManager = ord.OrderToMicroProcress(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA)
    
    OrderManager.waitingJumper(1)
    
    OrderManager.moovToSimple(1.5,0)
    
    log.logMessage(2,"scenario finished", 0)
    
def scenarioGreenStartPushingCake(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA):
    
    log.logMessage(2,"scenario DavinciBot : Pushing from GreenStart ", 0)
    
    OrderManager = ord.OrderToMicroProcress(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA)

    while pipeMainToMicro1.poll():
        pipeMainToMicro1.recv()
    OrderManager.waitingJumper(1)

    OrderManager.moovToSimple(1.5,0)

    while pipeMainToMicro1.recv():
        continue

    def move_back():
        yield MOV, 0, -5000 + 0x10000
    print('hey')
    pipeMainToMicro1.send((MOVEMENT, move_back, ()))

    log.logMessage(2,"scenario finished", 0)
    
def scenarioBlueStartPushingCake(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA):
    
    log.logMessage(2,"scenario DavinciBot : Pushing from BlueStart ", 0)
    
    OrderManager = ord.OrderToMicroProcress(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA)
    
    OrderManager.waitingJumper(1)
    
    OrderManager.moovToSimple(1.5,0)

    log.logMessage(2,"scenario finished", 0)

if __name__ == "__main__":
    pass
