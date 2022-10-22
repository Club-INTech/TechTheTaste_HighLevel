
from email.policy import strict
import sys, os

#path managing
sys.path.insert(1,os.path.join(os.path.dirname(__file__), '..', 'logLib'))

#import part
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
        log.logMessage(2, "start the camBot processus")

    def processCamMat(self):
        log.logMessage(2, "start the camMat processus")

    
    def config1(self): 
        log.logMessage(2, "start config1")
        procCamBot = Process(target = self.processCamBot)
        procCamMat = Process(target = self.processCamMat)
        procLIDAR = Process(target = self.processLIDAR)
        procMicro1 = Process(target = self.processMicro1)
        procMicro2 = Process(target = self.processMicro2)

        processList= [procCamBot, procCamMat, procLIDAR, procMicro1, procMicro2]
        for iter in range(len(processList)) :
            try :
                processList[iter].start()
            except :
                msg=  "process number" + str(iter) + " of the version" + str(self.version) + " failed to launch"
                log.Message(0,msg)
        
        return processList 

    
    
    def launch(self):
        log.logMessage(2, "start launching")
        if (self.version == 1):
            return self.config1()
            

if __name__ == "__main__" :
    starter = Launcher(1)
    list = starter.launch()

