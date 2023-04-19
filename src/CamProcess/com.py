import asyncio
import socket
import map
import logging

NUC_WELL_RECEIVED_ITEM = 0xFF
FLAG = [False, False]  # TCP, pipe
TCP = 0
PIPE = 1


def deserial(serialObsList):
    idObsList = serialObsList[0]
    ObsList = []
    serialObsList.pop(0)
    if (idObsList == 2):
        for datSet in range(0, len(serialObsList) - 1, 3):
            robot = map.Robot(serialObsList[datSet], serialObsList[datSet + 1], serialObsList[datSet + 2])
            ObsList.append(robot)
    elif (idObsList < 2):
        for datSet in range(0, len(serialObsList) - 1, 2):
            obs = map.Robot(serialObsList[datSet], serialObsList[datSet + 1])
            ObsList.append(obs)
    else:
        print("not a good main_id")
    return idObsList, ObsList


async def RxTCP(client, mapping):
    print("start RxTCP")
    Buffer = []

    nbrList = client.recv(4).decode()
    if nbrList != '':
        print("received!" + str(nbrList))
        FLAG[TCP] = True

    if FLAG[TCP]:
        for i in range(int(nbrList)):
            data = client.recv(4).decode()
            print("data received:" + data)
            Buffer.append(int(data))

        idObsList, obsList = deserial(Buffer)
        mapping.newObs(idObsList, obsList)


async def RxPipe(connLPA):
    print("started RxPipe")
    if connLPA.poll():
        FLAG[PIPE] = True


async def TxPipe(connLPA, mapping):
    print("started TxPipe")
    if FLAG[PIPE]:
        await RxPipe(connLPA)
        phyMap = mapping.getPhyMap()
        connLPA.send(phyMap)
        FLAG[PIPE] = False


async def main(HOST, PORT, connLPA):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # using IPv4 with TCP request
    try:
        client.connect((HOST, PORT))
        print("connection established!")
    except:
        print("connection refused")  # to do: use logging

    mapping = map.Mapping(40, 60)
    while True:
        task2 = asyncio.create_task(RxTCP(client, mapping))
        task1 = asyncio.create_task(TxPipe(connLPA, mapping))

        await task1
        await task2
        print("both task done")


if __name__ == '__main__':
    from multiprocessing import Pipe, Process

    HOST = socket.gethostname()
    PORT = 6512
    from time import sleep


    def procTest():
        while True:
            sleep(5)


    conn1, conn2 = Pipe()
    proc = Process(target=procTest)
    proc.start()

    # test of deserialisation
    serialList = [2, 42, 2500, 3600, 3, 58, 89, 74]
    deseriaList = deserial(serialList)
    for obj in deseriaList:
        print(obj)

    asyncio.run(main(HOST, PORT, conn1))