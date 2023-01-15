import time 
from hokuyolx import hokuyo

laser=hokuyo.HokuyoLX()

class Lili(object) :
    
    def __init__(self):
        self.dmin = 400
        self.group = 5
        self.state = 0
        
    def lidarstop(self, conn):
        '''Send a message to the main process if drobot < dmin'''
        self.state = 0
        while True : 
            data = laser.get_filtered_dist(grouping=self.group)
            Lr = []
            for i in range(len(data[1])):
                Lr.append(data[1][i][0])
            if min(Lr) < self.dmin and self.state == 0 : #stop the process
                laser.stop(conn)
                self.state = 1
            if min(Lr) > self.dmin and self.state == 1 : #retart the processus
                laser.restart(conn)
                self.state = 0
            time.sleep(1)
                
    def stop(self,conn):
        '''Send a message to the main process to stop the Agent'''
        conn.send(1)
        
    def restart(self,conn):
        '''Send a message to the main process to restart the Agent'''
        conn.send(0)