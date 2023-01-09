# this is a module with simple function to give order from main process to the microntroller process
#IRTC !!!!!
import sys, os
from multiprocessing import Pipe, Process
from math import sqrt, asin
#path managing
sys.path.insert(1,os.path.join(os.path.dirname(__file__), '..', 'utils'))

#import part
import log

#simple function to find the right angle

#work in the case where Yinit < Yfinal
def findAngleSimple(XInit,YInit,XFinal,YFinal):
    hyp = sqrt( (XFinal - XInit )**2 + (YFinal - YInit)**2 )
    opp = XInit - XFinal
    return asin(opp/hyp)

def findAngle(XInit,YInit,XFinal,YFinal):
    if YInit < YFinal :
        rslt = findAngleSimple(XInit,YInit,XFinal,YFinal)
    else :
        rslt = 3.14 - findAngleSimple(XInit,YInit,XFinal,YFinal)
    return rslt

#convert angle to ticks
def angleToTicks(angle):
    #not the final alpha of course
    alpha = 1
    return angle * alpha



class OrderToMicroProcress:
    def __init__(self,pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA):
        self.pipeToMicro1 = pipeMainToMicro1
        self.pipeToMicro2 = pipeMainToMicro2
        self.pipeToLPA = pipeMaintoLPA

    #4 methodes created in the case whe have to do an 
    # harder comunication protocol btwn our 2 process
    def sendDataToMicro1(self, data):
        self.pipeToMicro1.send(data)

    def sendDataToMicro2(self, data):
        self.pipeToMicro2.send(data)

    def receiveDataFromMicro1(self, data):
        return self.pipeToMicro1.recv()

    def receiveDataFromMicro1(self, data):
        return self.pipeToMicro2.recv()

    #this function send where the robot has to go (Xgoal, Ygoal) and then what is the next 
    #trajctory the robot has to do to get there
    def askLPAprocess(self, Xnow, Ynow, Xgoal, Ygoal):
        #we send the global trajectory we want to do
        self.pipeToLPA.send((Xnow,Ynow))
        self.pipeToLPA.send((Xgoal,Ygoal))
        #we get the next small steps we have to do
        Xstep,Ystep = self.pipeToLPA.recv()
        log.logMessage("robot is going to"+ str(Xstep) + ", " + str(Ystep))
        return (Xstep, Ystep)

    #all methods have clear name even though we could just need
    # one method instead of all of them. This way, it is easier 
    # to conceive the scenario

    #firstly we send the id of the order, look to the drive to
    #know which id correspond to wich order
    #then we send the necessary datas

    #blocking function that finish when juper is off
    def jumperState(self):
        jumper = False
        while(jumper):  
            jumper = True #read the state of the jumper and stock this value in the var jumper
            log.logMessage(3, "jumper on")
        return 1
        

    #to moov the robot to the point Xgoal,Ygoal
    def moovTo(self, Xgoal, Ygoal):
        Xinit, Yinit = self.getPosition()
        angle = findAngle(Xinit, Yinit, Xgoal, Ygoal)
        self.moovTurn(angle)
        #next function is a blocking mode function so wait for the action to be good
        self.smallMoovForward(sqrt( (Xgoal - Xinit)**2 + (Ygoal - Yinit)**2 ))
        

    #this function should only be used for small moov 
    # since it is only used without the LPA* process
    def smallMoovForward(self, ticks):
        self.sendDataToMicro1(1)
        self.sendDataToMicro1(ticks)
        #we wait until the moov is well done 


    def moovTurn(self, angle):
        self.sendDataToMicro1(2)
        ticks = angleToTicks(angle)
        self.sendDataToMicro1(ticks)
        #we wait until the moov is well done
        



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

    #order to track the position of the robot
    def getPosition(self):
        self.pipeToMicro1(11)
        if self.pipeToMicro1.poll(timeout=10):
            #return X,Y coordinate of the robot
            return self.pipeToMicro1.recv()
        else :
            log.logMessage(0,"position not received!")
            #maybe we should add something to face the error
            return 0

        
        