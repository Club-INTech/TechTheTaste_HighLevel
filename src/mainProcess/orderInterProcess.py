# this is a module with simple function to give order from main process to the microntroller process
# IRTC !!!!!
import sys
import os
import time
from multiprocessing import Pipe, Process
from math import sqrt, asin
# path managing
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..', 'utils'))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..', 'microProcess'))
# import part
import time
import log
from launcher import Xrobot, Yrobot, Hrobot, Arobot
from routine_sender import RoutineSender
from constants import *
from params import *
import math

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


class OrderToMicroProcress(RoutineSender):
    def __init__(self, pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA):
        super().__init__(Xrobot, Yrobot, Hrobot, pipeMainToMicro1, AXLE_TRACK_1A)
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
    #def moovTo(self, Xgoal, Ygoal):
    #do while (pos != goalpos)
    #    Xinit, Yinit = Xrobot.value, Yrobot.value
    #    while True:
    #        Xstep, Ystep = self.askLPAprocess(Xgoal, Ygoal)
    #        angle = findAngle(Xinit, Yinit, Xstep, Ystep)
    #        self.moovTurn(angle)
    #        #next function is a blocking mode function so wait for the action to be good
    #        self.smallMoovForward(sqrt( (Xstep - Xinit)**2 + (Ystep - Yinit)**2 ))
    #       if (Xgoal == Xrobot.value) and (Ygoal == Yrobot.value) :
    #            break

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
        
    
    #-----------------------------------------------------------------------------------------------------------------------------------------------------
    #------------------------------------------------------ new version ----------------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------------------------------------------------------------------
 
    
    # this function send where the robot has to go (Xgoal, Ygoal) and then what is the next
    # trajctory the robot has to do to get there
    def askLPAprocess(self, Xgoal, Ygoal):
        #we send the global trajectory we want to do
        self.pipeToLPA.send( [1, (Xgoal,Ygoal) ] )
        data = self.pipeToLPA.recv()
        Xstep,Ystep = data[1][0],data[1][1]
        self.indexes_to_coors(Xstep,Ystep)
        log.logMessage(2,"robot is going to ("+ str(Xstep) + "," + str(Ystep) + ")", 0)
        return Xstep, Ystep    
    
    def indexes_to_coors(self, i: int, j: int):
        """ Converts indices of the graph's vertex to the real life coordinates

        Args:
            i (int):
                First index of the vertex
            j (int):
                Second index of the vertex

        Returns:
            Tuple[float, float]: Real life coordinates
        """
        return float(i * RESOLUTION), float(j * RESOLUTION)
    
    def moovToSimple(self, X, Y):
        self.goto(X,Y)
        print(f'New position : {X,Y}')
        
    def moovToApproch(self, X, Y):
        step = 0.2
        self.goto(self, X - step,Y - step)
        print(f'New position : {X - step,Y - step}')
    
    def moovToLPA(self, Xgoal, Ygoal):
        #Xinit, Yinit = Xrobot.value, Yrobot.value
        #while True:
            #Xstep, Ystep = self.askLPAprocess(Xgoal, Ygoal)
            #Xstep, Ystep = self.indexes_to_coors(Xstep,Ystep)
        Xstep = 1
        Ystep = 1
        self.goto(Xstep,Ystep)
        #time.sleep(1)
        if (Xgoal == Xrobot.value) and (Ygoal == Yrobot.value) :
            return 1
        return 0
    
    def stopMoov(self):
        self.stop()
        print(f'Robot stop')
        
    def captureCake(self, x, y, slot):
        RIGHT, MID, LEFT = 1,2,3
        ecart = 0.15
        dx, dy = x - Xrobot.value, y - Yrobot.value
        magnitude = (dx * dx + dy * dy) ** .5
        d_theta = math.acos((1, -1)[False] * dx / magnitude) * (-1, 1)[dy >= 0] - Hrobot.value
        
        if slot == RIGHT:
            self.target(self, d_theta + math.atan(ecart/magnitude))
            self.goto(self, x, y)
        elif slot == MID:
            self.target(self, d_theta)
            self.goto(self, x, y)
        elif slot == LEFT:
            self.target(self, d_theta - math.atan(ecart/magnitude))
            self.goto(self, x, y)
    
    def releaseCake(self):
        step = 0.2
        self.goto(self, Xrobot.value - step, Yrobot.value - step, reverse=True)

    def moovCake(self, src, dest):
        RIGHT, MID, LEFT = 1,2,3
        LEFT_arm, RIGHT_arm = 1, -1
        UP_arm, DOWN_arm = -1, 1 
        ACTIVATE, DESACTIVATE = 1,0 #TODO change ByteMask
        
        if src == dest or (src, dest) not in {1,2,3}:
            pass
        else :
            #setting ARM to src
            if Arobot.value == src :
                pass
            
            elif abs(Arobot.value - src) == 1:
                if Arobot.value - src > 0:
                    self.ARMhorizontalPos(RIGHT_arm)
                else :
                    self.ARMhorizontalPos(LEFT_arm)
                    
                
            else : #abs(Arobot.value - src) == 2:
                if Arobot.value - src > 0:
                    self.ARMhorizontalPos(RIGHT_arm)
                    self.ARMhorizontalPos(RIGHT_arm)
                else :
                    self.ARMhorizontalPos(LEFT_arm)
                    self.ARMhorizontalPos(LEFT_arm)
            
            #updating ARM position        
            Arobot.value = src
            
            #uplifting genoise
            self.ARMverticalPos(position=DOWN_arm)
            self.PumpControll(ACTIVATE)
            self.ARMverticalPos(position=UP_arm)
            
            #ARM move to dest    
            if abs(Arobot.value - dest) == 1 :
                if Arobot.value - dest > 0 :
                    self.ARMhorizontalPos(RIGHT_arm)
                else :
                    self.ARMhorizontalPos(LEFT_arm)
        
                        
            else : #abs(Arobot.value - dest) == 2
                if Arobot.value - dest > 0 :
                    self.ARMhorizontalPos(RIGHT_arm)
                    self.ARMhorizontalPos(RIGHT_arm)
                else :
                    self.ARMhorizontalPos(LEFT_arm)
                    self.ARMhorizontalPos(LEFT_arm)
            
            #Deposit genoise
            self.ARMverticalPos(position = DOWN_arm)
            self.PumpControll(DESACTIVATE)
            self.ARMverticalPos(position = UP_arm)
            
            #updating ARM position 
            Arobot.value = dest
            
            
            
                
                    
            
                
                
                
        
        
    def sortCakePhase1(self, genoise, creme, glacage):
        left = genoise
        mid = creme
        right = glacage
        
        self.moovCake(self,right,left)
        
        self.moovCake(self,mid,left)
        self.moovCake(self,mid,left)
        
        self.moovCake(self,right,mid)
        self.moovCake(self,right,mid)
        
        self.moovCake(self,left,right)
        self.moovCake(self,left,right)
        
        self.moovCake(self,left,mid)
        
        self.moovCake(self,right,left)
        
        self.moovCake(self,mid,right)
        
        self.moovCake(self,mid,left)
    
    def sortCakePhase2(self, genoise, creme, glacage):
        left = genoise
        mid = creme
        right = glacage
        
        self.moovCake(self,right,left)
        self.moovCake(self,right,left)
        self.moovCake(self,right,left)
        
    def sortCakePhase3(self,genoise, creme, glacage):
        left = genoise
        mid = creme
        right = glacage
        
        self.moovCake(self,mid,left)
        self.moovCake(self,mid,left)
        self.moovCake(self,right,left)
        
    def putCherry(self,dest):
        self.place_cherry(self,dest)
        print(f'a cherry was placed on cake {dest}')
    
    def openCake(self, i):
        pass
    
    def lockCake(self, i):
        pass
    
    def activateCanon():
        pass
    
    #this function goal is to throw the cherry once bebouzator2 is at the good position
    def thrownCherry(self, waitingTime):
        maskActivateCanon_on = 0b00000001
        #                            |-> pump1 the one for the cannon on

        maskActivateCanon_off = 0b00000000
        self.Actuator2AControll(maskActivateCanon_on)
        time.sleep(waitingTime) #time to throw all the cherry
        self.Actuator2AControll(maskActivateCanon_off)

    #to grab the cherry
    def hooverActivation(self):
        maskActivateVaccum = 0b00000010
        #                            |-> pump2 for the hoover
        self.Actuator2AControll(maskActivateVaccum)

    def hooverDesactivate(self):
        maskActivateVaccum = 0b00000000
        self.Actuator2AControll(maskActivateVaccum)
        
