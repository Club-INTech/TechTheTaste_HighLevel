# this is a module with simple function to give order from main process to the microntroller process
#IRTC !!!!!
import sys, os
from multiprocessing import Pipe, Process

#path managing
sys.path.insert(1,os.path.join(os.path.dirname(__file__), '..', 'logLib'))

#import part
from logging import log

class OrderToMicroProcress:
    def __init__(self,pipeMainToMicro1, pipeMainToMicro2):
        self.pipeToMicro1 = pipeMainToMicro1
        self.pipeToMicro2 = pipeMainToMicro2

    #2 methodes created there in the case whe have to do an 
    # harder comunication protocol btwn our 2 process
    def sendDataToMicro1(self, data):
        self.pipeToMicro1.send(data)

    def sendDataToMicro2(self, data):
        self.pipeToMicro2.send(data)

    #all methods have clear name even though we could just need
    # one method instead of all of them. This way, it is easier 
    # to conceive the scenario

    #firstly we send the id of the order, look to the drive to
    #know which id correspond to wich order
    #then we send the necessary data

    #blocking function that finish when juper is off
    def jumperState(self):
        jumper = False
        while(jumper):  
            jumper = True
            #read the state of the jumper and stock this value in the var jumper
            
        return 1
        

    #ticks has to be on 16bits
    def moovForward(self, ticks):
        self.sendDataToMicro1(1)
        self.sendDataToMicro1(ticks)
        #warning! not finished!

    def moovTurn(self, ticks):
        self.sendDataToMicro1(2)
        self.sendDataToMicro1(ticks)
        #warning! not finished!

    def moovDeleted(self):
        self.pipeToMicro1(3)

    def motorActivatePos(self, idMotor, position):
        self.pipeToMicro2(4)
        self.pipeToMicro2(idMotor)
        self.pipeToMicro2(position)
        #Warning! not finished!

    def motorActivateTime(self, idMotor, time):
        self.pipeToMicro2(5)
        self.pipeToMicro2(idMotor)
        self.pipeToMicro2(time)
        #warning! not finished!

    #pump1,2,3 should only take the value 0 (off) or 1 (on)
    def pumpActualised(self, pump1, pump2, pump3):
        bitCode = pump1 | (pump2 << 1) | (pump3 << 2)

        self.pipeToMicro2(6)
        self.pipeToMicro2(bitCode)
        log.logMessage(3, "pump actualised")


    def trackingPos(self):
        self.pipeToMicro1(11)
        #warning! not finished!
        
        