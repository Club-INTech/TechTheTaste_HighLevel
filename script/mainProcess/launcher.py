from multiprocessing import Process

class Launcher :
    def __init__(self, version):
        self.version=version

    #pour chaque lancement de processus, il faut return le 
    #processus pour pouvoir bosser avec après
    def processLIDAR(self):
        print("start the lidar processus")

    def processMicro1(self):
        print("start the micro1 processus")

    def processMicro2(self):
        print("start the micro2 processus")

    def processCamBot(self):
        print("start the camBot process")

    def processCamMat(self):
        print("start the camMat processus")

    
    def config1(self): 
        print("start config1")
        self.processCamBot()
        self.processCamMat()
        self.processLIDAR()
        self.processMicro1()
        self.processMicro2()
    
    
    def launche(self):
        print("start launching")
        if (self.version == 1):
            self.config1()

if __name__ == "__main__" :
    starter = Launcher(1)
    starter.config1()

