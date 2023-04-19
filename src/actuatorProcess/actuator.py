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
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pinCanon, GPIO.OUT)
        GPIO.setup(pinVaccum, GPIO.OUT)
        GPIO.output(pinCanon, 0)
        GPIO.output(pinVaccum, 0)

    def run(self):
        while True :
            if self.pipeMain.poll() :
                order = self.pipeMain.recv()
                GPIO.output(order[0], order[1])
 