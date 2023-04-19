from math import sqrt

ROBOT_ID = 2
XMAX_ROBOT = 300  # in mm
YMAX_ROBOT = 300  # in mm


def length(x, y, X, Y):
    return sqrt(((x - X) ** 2) + ((y - Y) ** 2))


class Obs:
    def __init__(self, x, y):
        self.x = x  # in mm
        self.y = y  # in mm


class Robot:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y

    def phyActu(self, phyList, resX, resY):
        robotPhyObs = self.getPysical(resX, resY)
        for uni in robotPhyObs:
            phyList.append(uni)

    def getPysical(self, resX, resY):
        Xstep = 0  # in mm
        Ystep = 0  # in mm
        robotPhyList = []
        while Xstep < 2000:  # X axis of the cdr table

            while Ystep < 3000:  # Y axis of the cdr table

                if (length(self.x, self.y, Xstep, Ystep) < max(XMAX_ROBOT, YMAX_ROBOT)):
                    robotPhyList.append([Xstep, Ystep])
                Ystep = resY + Ystep
            Xstep = resX + Xstep
            Ystep = 0

        return robotPhyList


class Mapping:
    def __init__(self, resolutionX, resolutionY):
        self.robotId = ROBOT_ID
        self.mapListobj = [[], [], []]  # id=0 palets, id=1 cerise, id=2 robots
        self.mapPhy = []

        self.resX = resolutionX
        self.resY = resolutionY

    def newObs(self, idObs, obsList):
        self.mapListobj[idObs] = obsList

    def getPhyMap(self):
        self.mapPhy = []
        for bot in self.mapListobj[2]:
            if self.robotId != bot.id:
                bot.phyActu(self.mapPhy, self.resX, self.resY)
        return self.mapPhy


if __name__ == "__main__":

    import matplotlib.pyplot as plt
    import time

    start_time = time.time()

    cerise1 = Obs(15, 15)
    cerise2 = Obs(24, 700)
    lstCer = [cerise1, cerise2]

    Robot1 = Robot(0, 200, 600)
    Robot2 = Robot(1, 1050, 300)
    Robot3 = Robot(2, 1500, 2600)
    Robot4 = Robot(3, 1200, 800)
    lstRobot = [Robot1, Robot2, Robot3, Robot4]

    mapp = Mapping(40, 60)
    mapp.newObs(1, lstCer)
    mapp.newObs(2, lstRobot)

    phyMap = mapp.getPhyMap()
    lstObj = mapp.mapListobj

    print(time.time() - start_time)

    X = []
    Y = []
    for pos in phyMap:
        X.append(pos[0])
        Y.append(pos[1])

    plt.plot(X, Y, "ro")
    print(time.time() - start_time)
    plt.show()
    print(time.time() - start_time)
