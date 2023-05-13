# one function represents one scenario of the robot
# please, give clear name to the scenario so we they could be as useful as possible
import time
import orderInterProcess as ord
import sys, os
from multiprocessing import Pipe, Process

#path managing
sys.path.insert(1,os.path.join(os.path.dirname(__file__), '..', 'utils'))

#import part
import log
import math

#-----------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------ debugLidar part -----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------

    
def debugLidar(pipeMainToMicro1, pipeMainToMicro2, pipeMainToLPA, pipeLidarToMain):
    log.logMessage(2,"scenario debug of LIDAR", 0)
    while True :
        if pipeLidarToMain.poll():
            status = pipeLidarToMain.recv()
            print(status)
    
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------ test simple movement --------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------

    
def debugSimpleOrderStraight1(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA, pipeMainToActuator):
    log.logMessage(2,"scenario test simple order : Straight (1,0)", 0)
    
    OrderManager = ord.OrderToMicroProcress(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA, pipeMainToActuator)
   
    OrderManager.moovToSimple(0.5,0)
    
    log.logMessage(2,"simulation finished", 0)
    
def debugSimpleOrderStraight2(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA, pipeMainToActuator):
    log.logMessage(2,"scenario test simple order : Straight-left (0,1)", 0)
    
    OrderManager = ord.OrderToMicroProcress(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA, pipeMainToActuator)
   
    OrderManager.moovToSimple(0,0.5)
    
    log.logMessage(2,"simulation finished", 0)
    
def debugSimpleOrderStraight3(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA, pipeMainToActuator):
    log.logMessage(2,"scenario test simple order : Straight-right (0,1)", 0)
    
    OrderManager = ord.OrderToMicroProcress(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA, pipeMainToActuator)
   
    OrderManager.moovToSimple(0,-0.5)
    
    log.logMessage(2,"simulation finished", 0)
    
def debugSimpleOrderStraight4(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA, pipeMainToActuator):
    log.logMessage(2,"scenario test simple order : Straight-right (-1,0)", 0)
    
    OrderManager = ord.OrderToMicroProcress(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA, pipeMainToActuator)
   
    OrderManager.moovToSimple(-0.5,0)
    
    log.logMessage(2,"simulation finished", 0)

#-----------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------ debug Capture --------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------

def debugSimpleOrderCaptureCakeMid(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA, pipeMainToActuator):
    log.logMessage(2,"scenario test simple order : CaptureCakeMid (1,0)", 0)
    
    OrderManager = ord.OrderToMicroProcress(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA, pipeMainToActuator)
    
    RIGHT, MID, LEFT = 1,2,3
    x, y = 1, 0
    slot = MID
    OrderManager.captureCake(x, y, slot)
    
    log.logMessage(2,"simulation finished", 0)
    
def debugSimpleOrderCaptureCakeRight(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA, pipeMainToActuator):
    log.logMessage(2,"scenario test simple order : CaptureCakeRight (1,0)", 0)
    
    OrderManager = ord.OrderToMicroProcress(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA, pipeMainToActuator)
    
    RIGHT, MID, LEFT = 1,2,3
    x, y = 1, 0
    slot = RIGHT
    OrderManager.captureCake(x, y, slot)
    
    log.logMessage(2,"simulation finished", 0)

def debugSimpleOrderCaptureCakeLeft(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA, pipeMainToActuator):
    log.logMessage(2,"scenario test simple order : CaptureCakeLeft (1,0) ", 0)
    
    OrderManager = ord.OrderToMicroProcress(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA, pipeMainToActuator)
    
    RIGHT, MID, LEFT = 1,2,3
    x, y = 1, 0
    slot = LEFT
    OrderManager.captureCake(x, y, slot)
    
    log.logMessage(2,"simulation finished", 0)
    
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------ debug Actionneur2A -----------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------

def debugActioneur2A(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA, pipeMainToActuator):
    log.logMessage(2, "scenario test simple order: activate actuator", 0)
    OrderManager = ord.OrderToMicroProcress(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA, pipeMainToActuator)

    while True :
        OrderManager.VaccumActivate()
        OrderManager.CanonActivate()

        time.sleep(10)

        OrderManager.VaccumDesactivate()
        OrderManager.CanonDesactivate()

        time.sleep(10)
    

#-----------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------ scenario part --------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------

def scenarioSimpleGreen(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA, pipeMainToActuator):
    log.logMessage(2,"scenario simple", 0)
    
    OrderManager = ord.OrderToMicroProcress(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA, pipeMainToActuator)
    
    positionGlacage1, positionCreme1, positionGenoise1 = (0,0), (0,0), (0,0)
    positionGlacage2, positionCreme2, positionGenoise2 = (0,0), (0,0), (0,0)
    positionDeposit1, positionDeposit2 = (0,0), (0,0)
    positionEnd = (0,0)
    
    RIGHT, MID, LEFT = 1, 2, 3

    
    
    ########## First wave ############
    
    OrderManager.openCake(LEFT)
    OrderManager.openCake(MID)
    OrderManager.openCake(RIGHT)
   
    OrderManager.moovToSimple(positionGlacage1)
    OrderManager.captureCake(positionGlacage1,MID)
    OrderManager.lockCake(MID)
    
    OrderManager.moovToSimple(positionCreme1)
    OrderManager.captureCake(positionCreme1,LEFT)
    OrderManager.lockCake(LEFT)
    
    OrderManager.moovToSimple(positionGenoise1)
    OrderManager.captureCake(positionGenoise1,RIGHT)
    OrderManager.lockCake(RIGHT)
    
    #Phase 1
    
    OrderManager.moovToSimple(positionDeposit1)
    
    OrderManager.sortCakePhase1(genoise=RIGHT,creme=LEFT,glacage=MID)
    
    OrderManager.putCherry()
    OrderManager.openCake(RIGHT)
    OrderManager.releaseCake()
    
    #Phase 2
    
    OrderManager.moovToSimple(positionDeposit1) #a bit different
    
    OrderManager.sortCakePhase2(genoise=RIGHT,creme=LEFT,glacage=MID)
    
    OrderManager.putCherry()
    OrderManager.openCake(RIGHT)
    OrderManager.releaseCake()
    
    #Phase 3
    
    OrderManager.moovToSimple(positionDeposit1) #a bit different
    
    OrderManager.sortCakePhase3(genoise=RIGHT,creme=LEFT,glacage=MID)
    
    OrderManager.putCherry()
    OrderManager.openCake(RIGHT)
    OrderManager.releaseCake()
    
    ########## Second wave ############
    
    OrderManager.openCake(LEFT)
    OrderManager.openCake(MID)
    OrderManager.openCake(RIGHT)
    
    OrderManager.moovToSimple(positionGenoise2)
    OrderManager.captureCake(positionGenoise2,RIGHT)
    OrderManager.lockCake(RIGHT)
    
    OrderManager.moovToSimple(positionCreme2)
    OrderManager.captureCake(positionCreme2,LEFT)
    OrderManager.lockCake(LEFT)
    
    OrderManager.moovToSimple(positionGlacage2)
    OrderManager.captureCake(positionGlacage2, MID)
    OrderManager.lockCake(MID)
    
    #Phase 1
    
    OrderManager.moovToSimple(positionDeposit2)
    
    OrderManager.sortCakePhase1(genoise=RIGHT,creme=LEFT,glacage=MID)
    
    OrderManager.putCherry()
    OrderManager.openCake(RIGHT)
    OrderManager.releaseCake()
    
    #Phase 2
    
    OrderManager.moovToSimple(positionDeposit2) #a bit different
    
    OrderManager.sortCakePhase2(genoise=RIGHT,creme=LEFT,glacage=MID)
    
    OrderManager.putCherry()
    OrderManager.openCake(RIGHT)
    OrderManager.releaseCake()
    
    #Phase 3
    
    OrderManager.moovToSimple(positionDeposit2) #a bit different
    
    OrderManager.sortCakePhase3(genoise=RIGHT,creme=LEFT,glacage=MID)
    
    OrderManager.putCherry()
    OrderManager.openCake(RIGHT)
    OrderManager.releaseCake()
    
    OrderManager.moovToSimple(positionEnd)
    
    log.logMessage(2,"simulation finished", 0)


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
