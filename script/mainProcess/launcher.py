
import sys, os

sys.path.insert(1,os.path.join(os.path.dirname(__file__), '..', 'logLib'))

import log

from multiprocessing import Process

class Launcher :
    def __init__(self, version):
        self.version=version

    #pour chaque lancement de processus, il faut return le 
    #processus pour pouvoir bosser avec après
    def processLIDAR(self):
        log.logMessage(2, "start the lidar processus")

    def processMicro1(self):
        log.logMessage(2, "start the micro1 processus")

    def processMicro2(self):
        log.logMessage(2, "start the micro2 processus")

    def processCamBot(self):
        log.logMessage(2, "start the camBot process")

    def processCamMat(self):
        log.logMessage(2, "start the camMat processus")

    
    def config1(self): 
        log.logMessage(2, "start config1")
        self.processCamBot()
        self.processCamMat()
        self.processLIDAR()
        self.processMicro1()
        self.processMicro2()
    
    
    def launche(self):
        log.logMessage(2, "start launching")
        if (self.version == 1):
            self.config1()

if __name__ == "__main__" :
    starter = Launcher(1)
    starter.config1()

