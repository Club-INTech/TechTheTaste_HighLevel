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
    log.logMessage(2,"scenario debug of LPA*")
    
    OrderManager = ord.OrderToMicroProcress(pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA)
    
    log.logMessage(1, "orderManager created")

    OrderManager.askLPAprocess(0, 0, 1000, 1000)

    log.logMessage(2, "asked for a small moov") 

    OrderManager.askLPAprocess(0, 0, 1999, 2999)

    log.logMessage(2, "asked for a big moov") 

    time.sleep(2)

    #log.logMessage("simulation finished")
    
    print("simulation terminé")






if __name__ == "__main__":
    def readEsay(pipe1, pipe2):
        while True :
            print( "micro1: " + str(pipe1.recv()) )

    log.logMessage(1, "Start of debugg")
    main_micro1_pipe, micro1_main_pipe = Pipe()
    main_micro2_pipe, micro2_main_pipe = Pipe()

    scenar = Process( target = scenarioSimple, args = (main_micro1_pipe, main_micro2_pipe) )
    reader = Process( target = readEsay, args = (micro1_main_pipe, micro2_main_pipe) )

    scenar.start()
    reader.start()

    while True :
        time.sleep(10)