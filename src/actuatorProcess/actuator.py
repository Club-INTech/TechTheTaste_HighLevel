import RPi.GPIO as GPIO
from multiprocessing import Pipe, Process
import logging

FREQ = 10000
pinCanon = 12
pinVaccum = 16
powerCanon = 100
powerVaccum = 100


class actuatorProcess :

    def __init__(self, connPipeMain, logger):
        self.pipeMain = connPipeMain
        self.logger = logger
        GPIO.setup(pinCanon, GPIO.OUT)
        GPIO.setup(pinVaccum, GPIO.OUT)
        self.pwmCanon  = self.initPWM(pinCanon)
        self.pwmVaccum = self.initPWM(pinVaccum)

        self.pwmPowerCanon = [0, powerCanon] #managePower for Cannon(first list) and Vaccum (second list)
        self.pwmPowerVaccum = [0, powerVaccum]
    def initPWM(self, port):
        pwmObject = GPIO.PWM(port, FREQ)
        pwmObject.start(0) #init duty cycle = 0
        pwmObject.stop()
    
    def changePWM(self, pinPWM, pwmState):
        if (pinPWM == pinCanon) :
            self.pwmCanon.ChangeDutyCycle(self.pwmCanon[pwmState])
        elif (pinPWM == pinVaccum) :
            self.pwmVaccum.ChangeDutyCycle(self.pwmPowerVaccum[pwmState])


    def run(self):
        while True :
            if self.pipeMain.poll() :
                order = self.pipeMain.recv()
                self.changePWM(order[0], order[1])
                self.logger.info("change pwm of pin " + str(order[0]) + " to duty cycle " + str(order[1]))
 