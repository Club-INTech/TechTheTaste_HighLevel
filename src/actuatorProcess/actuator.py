import RPi.GPIO as GPIO
from multiprocessing import Pipe, Process
from time import sleep
import logging
#------ jumper           ------
pinVccJumper = 25

#------ cherry managment ------
FREQ = 10000
pinCanon = 12
pinVaccum = 16
powerCanon = 100
powerVaccum = 100

#----led managment ----------
pinLedGreen = 23

#servo management
pinServo = 17
openState = 12.5
closedState = 5.2

#------ stepper --------
pinIn1 = 2
pinIn2 = 3
pinIn3 = 5 
pinIn4 = 6

pinStepper = [pinIn1, pinIn2, pinIn3, pinIn4]

step_sequences= [[1,0,0,0],
                 [0,1,0,0],
                 [0,0,1,0],
                 [0,0,0,1]]


step_total = 450

class actuatorProcess :

    def __init__(self, connPipeMain, logger):
        self.pipeMain = connPipeMain
        self.logger = logger
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pinCanon, GPIO.OUT)
        GPIO.setup(pinVaccum, GPIO.OUT)
        GPIO.setup(pinVccJumper, GPIO.OUT)
        GPIO.output(pinVccJumper, 1) #used for data of the pin
        GPIO.output(pinCanon, 0)
        GPIO.output(pinVaccum, 0)

        GPIO.setup(pinLedGreen, GPIO.OUT)

        for pin in pinStepper :
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, 0)

        GPIO.output(pinLedGreen, 1)

        GPIO.setup(pinServo, GPIO.OUT)



        self.servo = GPIO.PWM(pinServo, 50)
        self.servo.start(closedState)

        self.openStepper()





    def ledLoop(self):
        while True:
            GPIO.output(pinLedGreen, 0)
            sleep(4)
            GPIO.output(pinLedGreen, 1)
            sleep(4)

    def openCloseServo(self, isOpen):
        if isOpen :
            self.servo.ChangeDutyCycle(openState)
        else : 
            self.servo.ChangeDutyCycle(closedState)

    def run(self):
        while True : 
            if self.pipeMain.poll() :
                order = self.pipeMain.recv()
                order_id = order[0]
                if order_id == 0:
                    GPIO.output(order[1], order[2])
                elif order_id == 1:
                    self.openCloseServo(order[1])
                elif order_id == 2:
                    self.ledLoop()
            sleep(0.1)
        
    def closeStepper(self):
        for step in range(step_total):
            for step_seq in step_sequences :
                for i in range(len(pinStepper)) :
                    GPIO.output(pinStepper[i],step_seq[i])
                sleep(0.01)

    def openStepper(self):
        for step in range(step_total):
            for step_seq in reversed(step_sequences) :
                for i in range(len(pinStepper)) :
                    GPIO.output(pinStepper[i],step_seq[i])
                sleep(0.01)
                    

            

if __name__ == "__main__":
    conn1, conn2 = Pipe()
    logger = logging.getLogger(__name__)
    proc = actuatorProcess(conn1, logger)
    #proc.ledLoop()

    proc.openCloseServo(True)
    sleep(4)
    proc.openCloseServo(False)


 