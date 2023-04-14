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

def scenarioSimple(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA):
    log.logMessage(2,"début du scenario!")
    OrderManager = ord.OrderToMicroProcress(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA)

    OrderManager.jumperState()
    log.logMessage(1,"start of the match!!!")

    OrderManager.moovForward(3000)
    log.logMessage(1,"avancé de 3000 ticks")

    time.sleep(2)
    log.logMessage(1,"attendue 20 secondes")

    OrderManager.moovForward(-3000)
    log.logMessage(1,"reculé de 3000 ticks")

    log.logMessage(1,"scenario terminé!")
    return 1


#-----------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------ debug part -----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------

def debugLidarProc(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA):
    log.logMessage(2,"scenario debug of LPA*", 0)
    
    OrderManager = ord.OrderToMicroProcress(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA)
    
    log.logMessage(1, "orderManager created", 0)

    OrderManager.askLPAprocess(1000, 1000)

    log.logMessage(2, "asked for a small moov", 0) 

    OrderManager.askLPAprocess(1999, 2999)

    log.logMessage(2, "asked for a big moov", 0) 

    time.sleep(2)

    log.logMessage(2,"simulation finished", 0)
    
def debugLidar(pipeMainToMicro1, pipeMainToMicro2, pipeMainToLPA, pipeLidarToMain):
    log.logMessage(2,"scenario debug of LIDAR", 0)
    while True :
        if pipeLidarToMain.poll():
            status = pipeLidarToMain.recv()
            print(status)
            
def debugRaspy(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA):
    log.logMessage(2,"scenario debug of LPA*", 0)
    
    OrderManager = ord.OrderToMicroProcress(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA)
    
    log.logMessage(1, "orderManager created", 0)

    OrderManager.askLPAprocess(1000, 1000)

    log.logMessage(2, "asked for a small moov", 0) 

    OrderManager.askLPAprocess(1999, 2999)

    log.logMessage(2, "asked for a big moov", 0) 

    time.sleep(2)

    log.logMessage(2,"simulation finished", 0)
    
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------ test movement --------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------

    
def debugSimpleOrderStraight1(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA):
    log.logMessage(2,"scenario test simple order : Straight (1,0)", 0)
    
    OrderManager = ord.OrderToMicroProcress(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA)
   
    OrderManager.moovToSimple(0.5,0)
    
    log.logMessage(2,"simulation finished", 0)
    
def debugSimpleOrderStraight2(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA):
    log.logMessage(2,"scenario test simple order : Straight-left (0,1)", 0)
    
    OrderManager = ord.OrderToMicroProcress(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA)
   
    OrderManager.moovToSimple(0,0.5)
    
    log.logMessage(2,"simulation finished", 0)
    
def debugSimpleOrderStraight3(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA):
    log.logMessage(2,"scenario test simple order : Straight-right (0,1)", 0)
    
    OrderManager = ord.OrderToMicroProcress(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA)
   
    OrderManager.moovToSimple(0,-0.5)
    
    log.logMessage(2,"simulation finished", 0)
    
def debugSimpleOrderStraight4(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA):
    log.logMessage(2,"scenario test simple order : Straight-right (-1,0)", 0)
    
    OrderManager = ord.OrderToMicroProcress(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA)
   
    OrderManager.moovToSimple(-0.5,0)
    
    log.logMessage(2,"simulation finished", 0)

def debugSimpleOrderTurn(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA):
    log.logMessage(2,"scenario test simple order : Turn (pi/2)", 0)
    
    OrderManager = ord.OrderToMicroProcress(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA)
   
    OrderManager.turn(math.pi/2)
    
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
    
    greenSidePositionGlacage1, greenSidePositionCreme1, positionGenoise1 = (0,0), (0,0), (0,0)
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
    
    log.logMessage(2,"scenario DavinciBot approval : leaving and going back to the depart zone ", 0)
    
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
    def readEsay(pipe1, pipe2):
        while True :
            print( "micro1: " + str(pipe1.recv()) )

    log.logMessage(1, "Start of debugg", 0)
    main_micro1_pipe, micro1_main_pipe = Pipe()
    main_micro2_pipe, micro2_main_pipe = Pipe()

    scenar = Process( target = scenarioSimple, args = (main_micro1_pipe, main_micro2_pipe) )
    reader = Process( target = readEsay, args = (micro1_main_pipe, micro2_main_pipe) )

    scenar.start()
    reader.start()

    while True :
        time.sleep(10)
