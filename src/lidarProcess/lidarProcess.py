import sys, os
import time
from hokuyolx import hokuyo

#sys.path.insert(1,os.path.join(os.path.dirname(__file__), '..', 'utils'))
#from params import __param_getter, paramlidar

group = 3
dmin = 50
DMAX = 2000
BORD = 20

#laser=hokuyo.HokuyoLX()

#data = laser.get_dist(grouping=group)
#print(data)

class Lili(object) :
    
    def __init__(self):
        self.state = 0
        self.laser = hokuyo.HokuyoLX()
        
    def lidarstop(self, conn) -> None:
        '''Send a message to the main process if drobot < dmin'''
        self.state = 0
        while True : 
            timestamp, data = self.laser.get_filtered_dist(dmax=DMAX)
            Lr = []
            for i in range(len(data[1])):
                Lr.append(data[1][i])
            Lr = Lr[BORD:-BORD]
            
            if not Lr:
                pass
            else :
                minlr = min(Lr)
                print('distance =', minlr)
                if minlr < dmin and self.state == 0 : #stop the process
                    self.stop(conn)
                    self.state = 1
                elif minlr > dmin and self.state == 1 : #retart the processus
                    self.restart(conn)
                    self.state = 0
            time.sleep(0.001)
                
    def stop(self,conn) -> None:
        '''Send a message to the main process to stop the Agent'''
        conn.send(1)
        
    def restart(self,conn) -> None:
        '''Send a message to the main process to restart the Agent'''
        conn.send(0)
