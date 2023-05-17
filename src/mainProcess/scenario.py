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
    
    OrderManager.waitingJumper(1)
   
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
#------------------------------------------------------ debug Actionneur2A -----------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------

def debugActioneur2A(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA, pipeMainToActuator):
    log.logMessage(2, "scenario test simple order: activate actuator", 0)
    OrderManager = ord.OrderToMicroProcress(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA, pipeMainToActuator)

    OrderManager.VaccumActivate()
    time.sleep(10)
    OrderManager.VaccumDesactivate()
    time.sleep(5)
    OrderManager.CanonActivate()
    OrderManager.ServoOn()
    time.sleep(5)
    OrderManager.ServoOff()
    time.sleep(2)
    OrderManager.CanonDesactivate()
    OrderManager.ledOn()

def homolog2A(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA, pipeMainToActuator):
    log.logMessage(2, "scenario test simple order: activate actuator", 0)
    OrderManager = ord.OrderToMicroProcress(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA, pipeMainToActuator)   
    OrderManager.waitingJumper(1) 

def simpleScenar2A(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA, pipeMainToActuator):
    log.logMessage(2, "scenario test simple order: activate actuator", 0)
    OrderManager = ord.OrderToMicroProcress(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA, pipeMainToActuator)
    
    #put the cherries
    OrderManager.moovToSimple(0.5,1.5)
    OrderManager.moovToSimple(0.5, 2.5)
    time.sleep(5)
    OrderManager.CanonActivate()
    OrderManager.ServoOn()
    time.sleep(5)
    OrderManager.ServoOff()
    OrderManager.CanonDesactivate()

    #come back to position
    OrderManager.moovToSimple(0.25, 2)
    OrderManager.ledOn()

def ambiScenar2A(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA, pipeMainToActuator):
    log.logMessage(2, "scenario test simple order: activate actuator", 0)
    
    #get new cherry
    OrderManager = ord.OrderToMicroProcress(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA, pipeMainToActuator)
    OrderManager.moovToSimple(0.5,0.5)
    OrderManager.VaccumActivate()
    OrderManager.moovToSimple(0.5,1.5)
    time.sleep(10)
    OrderManager.VaccumDesactivate()


    #put the cherries
    OrderManager.moovToSimple(0.5, 2.5)
    time.sleep(5)
    OrderManager.CanonActivate()
    OrderManager.ServoOn()
    time.sleep(5)
    OrderManager.ServoOff()
    OrderManager.CanonDesactivate()

    #come back to position
    OrderManager.moovToSimple(0.25, 2)
    OrderManager.ledOn()



#-----------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------ scenario part --------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------

def scenario_green_1(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA, pipeMainToActuator):
    
    log.logMessage(2, "scenario green 1", 0)
    
    OrderManager = ord.OrderToMicroProcress(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA, pipeMainToActuator)
    
    #Dépôt des cerises
    OrderManager.CanonActivate()
    OrderManager.ServoOn()
    time.sleep(5)
    OrderManager.ServoOff()
    OrderManager.CanonDesactivate()
    
    #Poussage de 2 piles de génoises
    OrderManager.moovToSimple(-0.45,0)
    time.sleep(5)
    OrderManager.moovToSimple(-1.65,0)
    time.sleep(5)
    
    #Récupération des cerises
    OrderManager.moovToSimple(-1.125,0,True)
    time.sleep(5)
    
    OrderManager.moovToSimple(-1.125,-0.1)
    time.sleep(5)
    OrderManager.VaccumActivate()
    time.sleep(1)
    
    OrderManager.moovToSimple(-1.165,-0.1)
    time.sleep(5)
    
    OrderManager.moovToSimple(0,0)
    time.sleep(5)
    
    #Dépot des cerises
    OrderManager.CanonActivate()
    OrderManager.ServoOn()
    time.sleep(5)
    OrderManager.ServoOff()
    OrderManager.CanonDesactivate()
    
    #Allumage des leds
    OrderManager.ledOn()
    
def scenario_blue_1(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA, pipeMainToActuator):
    
    log.logMessage(2, "scenario green 1", 0)
    
    OrderManager = ord.OrderToMicroProcress(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA, pipeMainToActuator)
    
    #Dépôt des cerises
    OrderManager.CanonActivate()
    OrderManager.ServoOn()
    time.sleep(5)
    OrderManager.ServoOff()
    OrderManager.CanonDesactivate()
    
    #Poussage de 2 piles de génoises
    OrderManager.moovToSimple(-0.45,0)
    time.sleep(5)
    OrderManager.moovToSimple(-1.65,0)
    time.sleep(5)
    
    #Récupération des cerises
    OrderManager.moovToSimple(-1.125,0,True)
    time.sleep(5)
    
    OrderManager.moovToSimple(-1.125,0.1)
    time.sleep(5)
    OrderManager.VaccumActivate()
    time.sleep(1)
    
    OrderManager.moovToSimple(-1.165,0.1)
    time.sleep(5)
    
    OrderManager.moovToSimple(0,0)
    time.sleep(5)
    
    #Dépot des cerises
    OrderManager.CanonActivate()
    OrderManager.ServoOn()
    time.sleep(5)
    OrderManager.ServoOff()
    OrderManager.CanonDesactivate()
    
    #Allumage des leds
    OrderManager.ledOn()
    


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
