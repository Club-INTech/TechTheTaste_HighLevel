import sys, os
import time
from hokuyolx import hokuyo
import math

group = 3
dmin = 500
DMAX = 2000
BORD = 25


def linera_interpolate(t, a, b, x, y):
    """t is between a and b, result is between x and y"""
    return (t - a) / (b - a) * (y - x) + x

class Lili:
    # champs de vision: [ -135 °, 135 ° ]

    log = False

    def __init__(self):
        self.state = 0
        self.laser = hokuyo.HokuyoLX()
        print(self.laser.amin, self.laser.amax)
        print(self.laser.get_angles(grouping=1080) * 180 / math.pi)

    def lidarstop(self, conn) -> None:
        '''Send a message to the main process if drobot < dmin'''
        self.state = 0
        while True:
            timestamp, data = self.laser.get_filtered_dist(start=int(linera_interpolate(-90, -135, 135, 0, 1080)), end=int(linera_interpolate(90, -135, 135, 0, 1080)), dmax=DMAX)
            Lr = []
            print(data[0, :] * 180 / math.pi)
            for i in range(BORD, len(data)-BORD):
                d = data[i][0]
                # if -1.175 < d  and d < 1.175 :
                Lr.append(data[i][1])
            
            if not Lr:
                pass
            else :
                minlr = min(Lr)
                if self.log:
                    print(f'Limite {dmin} : distance = ', minlr)
                if minlr < dmin and self.state == 0 : #stop the process
                    self.stop(conn)
                    self.state = 1
                elif minlr > dmin and self.state == 1 : #retart the processus
                    self.restart(conn)
                    self.state = 0
            time.sleep(0.1)

    def display_vision(self, chars=30):
        proximity = ' ░▒▓█'
        proximity2 = ' º•°×÷*■█'

    def lidarstop2(self, conn, Xrobot, Yrobot, Hrobot, color) -> None:
        '''Send a message to the main process if drobot < dmin'''
        
        if color == 1 :
            Xlimit1, Xlimit2 = 0, 3  
            Ylimit1, Ylimit2 = -2, 0
        else : 
            Xlimit1, Xlimit2 = 0, 3  
            Ylimit1, Ylimit2 = 0, 2
        
        self.state = 0
        while True : 
            timestamp, data = self.laser.get_filtered_dist(dmax=DMAX)
            
            Lr = data[0][BORD:-BORD]
            minlr = data[0][BORD]
            minj = BORD
            for i in range(len(Lr)):
                if data[0][i] < minlr:
                    minlr = data[0][i]
                    minj = i
            
            Xobstacle = Lr[minj] * math.cos(data[1][minj])
            Yobstacle = Lr[minj] * math.sin(data[1][minj])
            
            x,y = self.rotate((Xobstacle,Yobstacle), (Xrobot,Yrobot), Hrobot)
            
            if not Lr:
                pass
            
            else :
                if minlr < dmin and self.state == 0 : #stop the process
                    if Xlimit1 < (x + Xrobot) and (x + Xrobot) < Xlimit2 :
                        if Ylimit1 < (y + Yrobot) and (y + Yrobot) < Ylimit2 :
                            self.stop(conn)
                            self.state = 1
                elif minlr > dmin and self.state == 1 : #retart the processus
                    self.restart(conn)
                    self.state = 0
            time.sleep(1)

    def rotate(M, O, angle):
        xM, yM, x, y = M[0] - O[0], M[1] - O[1], 0, 0
        angle *= math.pi / 180
        x = xM * math.cos(angle) + yM * math.sin(angle) + O[0]
        y = -xM * math.sin(angle) + yM * math.cos(angle) + O[1]
        return x,y

                
    def stop(self,conn) -> None:
        '''Send a message to the main process to stop the Agent'''
        conn.send(1)
        
    def restart(self,conn) -> None:
        '''Send a message to the main process to restart the Agent'''
        conn.send(0)


if __name__ == "__main__":
    from multiprocessing import Pipe
    conn1, conn2 = Pipe()
    lidar = Lili()
    lidar.log = True
    lidar.lidarstop(conn1)
    

