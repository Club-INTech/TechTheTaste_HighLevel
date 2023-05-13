import RPi.GPIO as GPIO
from multiprocessing import Pipe, Process
from time import sleep
import logging

#------ cherry managment ------
FREQ = 10000
pinCanon = 12
pinVaccum = 16
powerCanon = 100
powerVaccum = 100

#----led managment ----------
pinLedRed = 23
pinLedGreen = 24
pinLedBlue = 25

#servo management
pinServo = 17
openState = 10
closedState = 7.5

class actuatorProcess :

    def __init__(self, connPipeMain, logger):
        self.pipeMain = connPipeMain
        self.logger = logger
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pinCanon, GPIO.OUT)
        GPIO.setup(pinVaccum, GPIO.OUT)
        GPIO.output(pinCanon, 0)
        GPIO.output(pinVaccum, 0)

        GPIO.setup(pinLedRed, GPIO.OUT)
        GPIO.setup(pinLedBlue, GPIO.OUT)
        GPIO.setup(pinLedGreen, GPIO.OUT)
        GPIO.output(pinLedRed, 1)
        GPIO.output(pinLedGreen, 1)
        GPIO.output(pinLedBlue, 1)

        GPIO.setup(pinServo, GPIO.OUT)
        self.servo = GPIO.PWM(pinServo, 50)
        self.servo.start(7.5)



    def run(self):
        while True :
            if self.pipeMain.poll() :
                order = self.pipeMain.recv()
                GPIO.output(order[0], order[1])
                sleep(0.1)

    def ledLoop(self):
        while True:
            GPIO.output(pinLedRed, 0)
            sleep(1)
            GPIO.output(pinLedRed, 1)
            sleep(1)

    def openCloseServo(self, isOpen):
        if isOpen :
            self.servo.ChangeDutyCycle(openState)
        else : 
            self.servo.ChangeDutyCycle(closedState)

    def orderManager(self):
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
                    

            

if __name__ == "__main__":
    conn1, conn2 = Pipe()
    logger = logging.getLogger(__name__)
    proc = actuatorProcess(conn1, logger)
    #proc.ledLoop()

    proc.openCloseServo(True)
    sleep(4)
    proc.openCloseServo(False)


 