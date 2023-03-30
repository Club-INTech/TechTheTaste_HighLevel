# this is a module with simple function to give order from main process to the microntroller process
# IRTC !!!!!
import sys
import os
from multiprocessing import Pipe, Process
from math import sqrt, asin
# path managing
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..', 'utils'))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..', 'microProcess'))
# import part
import log
from launcher import Xrobot,Yrobot
from constants import *

# simple function to find the right angle

# work in the case where Yinit < Yfinal
def findAngleSimple(XInit, YInit, XFinal, YFinal):
    hyp = sqrt((XFinal - XInit)**2 + (YFinal - YInit)**2)
    opp = XInit - XFinal
    return asin(opp/hyp)


def findAngle(XInit, YInit, XFinal, YFinal):
    if YInit < YFinal:
        rslt = findAngleSimple(XInit,YInit,XFinal,YFinal)
    else:
        rslt = 3.14 - findAngleSimple(XInit,YInit,XFinal,YFinal)
    return rslt

# convert angle to ticks
def angleToTicks(angle):
    # not the final alpha of course
    alpha = 1
    return angle * alpha


class OrderToMicroProcress:
    def __init__(self, pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA):
        self.pipeToMicro1 = pipeMainToMicro1
        self.pipeToMicro2 = pipeMainToMicro2
        self.pipeToLPA = pipeMaintoLPA

    # 4 methodes created in the case whe have to do an
    # harder comunication protocol btwn our 2 process
    def sendDataToMicro1(self, data):
        self.pipeToMicro1.send(data)

    def sendDataToMicro2(self, data):
        self.pipeToMicro2.send(data)

    def receiveDataFromMicro1(self, data):
        return self.pipeToMicro1.recv()

    def receiveDataFromMicro2(self, data):
        return self.pipeToMicro2.recv()

    # this function send where the robot has to go (Xgoal, Ygoal) and then what is the next
    # trajctory the robot has to do to get there
    def askLPAprocess(self, Xgoal, Ygoal):
        #we send the global trajectory we want to do
        self.pipeToLPA.send( [1, (Xgoal,Ygoal) ] )
        data = self.pipeToLPA.recv()
        print(data)
        Xstep,Ystep = data[0],data[1]
        log.logMessage(2,"robot is going to ("+ str(Xstep) + "," + str(Ystep) + ")", 0)
        return Xstep, Ystep


    # all methods have clear name even though we could just need
    # one method instead of all of them. This way, it is easier 
    # to conceive the scenario

    # firstly we send the id of the order, look to the drive to
    # know which id correspond to wich order
    # then we send the necessary datas

    # blocking function that finish when juper is off
    def jumperState(self):
        jumper = False
        while(jumper):  
            jumper = True #read the state of the jumper and stock this value in the var jumper
            log.logMessage(3, "jumper on", 0)

        return 1

    # to moov the robot to the point Xgoal,Ygoal
    def moovTo(self, Xgoal, Ygoal):
    #do while (pos != goalpos)
        Xinit, Yinit = Xrobot.value, Yrobot.value
        while True:
            Xstep, Ystep = self.askLPAprocess(Xgoal, Ygoal)
            angle = findAngle(Xinit, Yinit, Xstep, Ystep)
            self.moovTurn(angle)
            #next function is a blocking mode function so wait for the action to be good
            self.smallMoovForward(sqrt( (Xstep - Xinit)**2 + (Ystep - Yinit)**2 ))
            if (Xgoal == Xrobot.value) and (Ygoal == Yrobot.value) :
                break
    
    # this function should only be used for small moov
    # since it is only used without the LPA* process
    def smallMoovForward(self, ticks):
        self.sendDataToMicro1((MOVEMENT, goto(0,ticks)))
        # we wait until the moov is well done

    def moovTurn(self, angle):
        #TODO delete ?
        #self.sendDataToMicro1(2)
        ticks = angleToTicks(angle)
        self.sendDataToMicro1((MOVEMENT,goto(ticks,0))) #2
        # we wait until the moov is well done

    def moovDeleted(self):
        self.pipeToMicro1(3)

    def motorActivatePos(self, idMotor, position):
        self.pipeToMicro2(4)
        self.pipeToMicro2(idMotor)
        self.pipeToMicro2(position)
        # Warning! not finished!

    def motorActivateTime(self, idMotor, time):
        self.pipeToMicro2(5)
        self.pipeToMicro2(idMotor)
        self.pipeToMicro2(time)
        # warning! not finished!

    # pump 1,2,3 should only take the value 0 (off) or 1 (on)
    def pumpActualised(self, pump1, pump2, pump3):
        bitCode = pump1 | (pump2 << 1) | (pump3 << 2)

        self.pipeToMicro2(6)
        self.pipeToMicro2(bitCode)
        log.logMessage(3, "pump actualised", 0)

    def goto(angle, magnitude):
        yield CAN, 0, 0
        yield ROT, 0, angle + 0x10000 * (angle < 0)
        yield MOV, 0, magnitude + 0x10000 * (magnitude < 0)

        
        
