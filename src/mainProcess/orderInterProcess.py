# this is a module with simple function to give order from main process to the microntroller process
# IRTC !!!!!
import sys
import os
import time
from multiprocessing import Pipe, Process
import RPi.GPIO as GPIO 
from math import sqrt, asin
# path managing
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..', 'utils'))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..', 'microProcess'))
# import part
import time
import log
from launcher import Xrobot, Yrobot, Hrobot, Xarm, Yarm
from routine_sender import RoutineSender
from constants import *
from params import *
import math

class OrderToMicroProcress(RoutineSender):
    def __init__(self, pipeMainToMicro1, pipeMainToMicro2, pipeMaintoLPA):
        super().__init__(Xrobot, Yrobot, Hrobot, Xarm, [(1, ), (1, ), (1,)], pipeMainToMicro1, AXLE_TRACK_1A)
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
    
    def moovToSimple(self, X, Y, reversed=False):
        self.goto(X,Y,reversed)
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
    
    def turn(self, angle):
        self.target(angle)
    
    def stopMoov(self):
        self.stop()
        print(f'Robot stop')
        
    def captureCake(self, x, y, slot):
        RIGHT, MID, LEFT = 1,2,3
        adjustement = 0.12
        
        dx, dy = x - Xrobot.value, y - Yrobot.value
        magnitude = (dx * dx + dy * dy) ** .5
        
        if slot == RIGHT:
            alpha1 = math.acos(dx/magnitude)
            
            magnitude2 = (adjustement**2 + magnitude**2)**0.5
            alpha2 = math.acos(magnitude/magnitude2)
            
            x = x + math.cos(alpha1 + alpha2)
            y = y + math.sin(alpha1 + alpha2)
            
            dx, dy = x - Xrobot.value, y - Yrobot.value
            magnitude = (dx * dx + dy * dy) ** .5
            magnitude_adjusted = magnitude2 - adjustement
            
            x_right = x - (dx - magnitude_adjusted * math.cos(magnitude_adjusted/dx))
            y_right = x - (dy - magnitude_adjusted * math.cos(magnitude_adjusted/dy))
            self.goto(self, x_right, y_right)
            
        elif slot == MID:
            magnitude_adjusted = magnitude - adjustement
            x_mid = x - (dx - magnitude_adjusted * math.cos(magnitude_adjusted/dx))
            y_mid = x - (dy - magnitude_adjusted * math.cos(magnitude_adjusted/dy))
            self.goto(self, x_mid, y_mid)
            
        elif slot == LEFT:
            alpha1 = math.acos(dx/magnitude)
            
            magnitude2 = (adjustement**2 + magnitude**2)**0.5
            alpha2 = math.acos(magnitude/magnitude2)
            
            x = x + math.cos(alpha1 - alpha2)
            y = y + math.sin(alpha1 - alpha2)
            
            dx, dy = x - Xrobot.value, y - Yrobot.value
            magnitude = (dx * dx + dy * dy) ** .5
            magnitude_adjusted = magnitude2 - adjustement
            
            x_left = x - (dx - magnitude_adjusted * math.cos(magnitude_adjusted/dx))
            y_left = x - (dy - magnitude_adjusted * math.cos(magnitude_adjusted/dy))
            self.goto(self, x_left, y_left)
            
    
    def releaseCake(self):
        step = 0.2
        self.goto(self, Xrobot.value - step, Yrobot.value - step, reverse=True)

    #LEFT, MIDDLE, RIGHT = -1400, 700, 0
    def moovCake(self, src, dest):
        self.move_cake(src,dest)
            
    def sortCakePhase1(self, genoise, creme, glacage):
        left = genoise
        mid = creme
        right = glacage
        
        self.moovCake(right,left)
        
        self.moovCake(mid,left)
        self.moovCake(mid,left)
        
        self.moovCake(right,mid)
        self.moovCake(right,mid)
        
        self.moovCake(left,right)
        self.moovCake(left,right)
        
        self.moovCake(left,mid)
        
        self.moovCake(right,left)
        
        self.moovCake(mid,right)
        
        self.moovCake(mid,left)
    
    def sortCakePhase2(self, genoise, creme, glacage):
        left = genoise
        mid = creme
        right = glacage
        
        self.moovCake(right,left)
        self.moovCake(right,left)
        self.moovCake(right,left)
        
    def sortCakePhase3(self,genoise, creme, glacage):
        left = genoise
        mid = creme
        right = glacage
        
        self.moovCake(mid,left)
        self.moovCake(mid,left)
        self.moovCake(right,left)
        
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
        
    def waitingJumper(self, edge=1):
        EDGES = [ [True, False], [False, True]]
        EDGE = EDGES[edge] #select the edge

        GPIO.setmode(GPIO.BCM)
        jumper = 24 #digital Output

        GPIO.setup(jumper, GPIO.IN)
        ctn = True
        while ctn:
            ctn = EDGE[ GPIO.input(jumper)]
            print("waiting jumper")
            #log.logMessage(3, "waiting jumper", 0) 
