import asyncio
import socket
import map
import logging
import time
import sys

NUC_WELL_RECEIVED_ITEM = '0xFF'


def getSerialData(listObj):
    serialData = [listObj[0]]
    if listObj[0] == 2 :
        listObj.pop(0)
        for obj in listObj :
            serialData.append(obj.x)
            print("added: " + str(obj.x))
            serialData.append(obj.y)
            print("added: " + str(obj.y))
            serialData.append(obj.id)
            print("added: " + str(obj.id))
    elif (listObj[0] < 2):
        listObj.pop(0)
        for obj in listObj :
            serialData.append(obj.x)
            print("added: " + str(obj.x))
            serialData.append(obj.y)
            print("added: " + str(obj.y))
    serialData.insert(0, len(serialData))
    return serialData

def sendableData(data): #data is an int 
    data = str(data)
    length = sys.getsizeof(data) - 49
    if (length == 1):
        data = "000"+ data
        return data.encode()
    if (length == 2):
        data = "00"+ data
        return data.encode()
    if (length == 3):
        data = "0" + data
        return data.encode()
    if (length == 4):
        return data.encode()
    else :
        print("erorr!!!!!")

def initServer(host, port) :
    server = socket.socket()
    server.bind((host, port))
    server.listen(2)
    print("init done")
    return server

def TxTCP(connTCP, listObs):
    serialData = getSerialData(listObs)
    for data in serialData:
        print("dataToSend: " + str(data))
        dataSTR = sendableData(data)
        connTCP.send(dataSTR)

def RxTCP(connTCP):
    while True :
        data = connTCP.recv(2).decode()
        print("data:" + str(data))
        if data == NUC_WELL_RECEIVED_ITEM :
            break

def main(connLPA, server):
    connTCP, address = server.accept() 

    while True:
        if connLPA.poll():
            listObs = connLPA.recv()
            if isinstance(listObs, list):
                print("main: received a list!")
                TxTCP(connTCP, listObs)
            else :
                print("error! should only received list")
        else :
            time.sleep(0.001)



if __name__ == '__main__':
    from multiprocessing import Pipe, Process
    HOST = socket.gethostname()
    PORT = 6512
    print(HOST)
    class Obj:
        def __init__(self, x ,y, id):
            self.x = x
            self.y = y
            self.id = id

    obj1 = Obj(15,3556,26)
    obj2 = Obj(15,3556,15)
    obj3 = Obj(15,3556,264)
    obj4 = Obj(15,3556,314)


    def procTest( conn):
        while True:
            conn.send(45)
            conn.send("yo!!!!!!!!!!!")
            conn.send([2, obj1, obj2, obj3, obj4])
            time.sleep(500)
            
    conn1, conn2 = Pipe()
    proc = Process(target=procTest, args= (conn2,))
    proc.start()
    server = initServer(HOST, PORT)
    main(conn1, server)
    