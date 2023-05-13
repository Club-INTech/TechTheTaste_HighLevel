from multiprocessing import Pipe

OFF = 0
ON = 1

pinCanon = 12
pinVaccum = 16

#API:
#shape of an order through the conn: [order_id, arg1, arg2]
#controll a pin for vaccum or cannon:
#    order_id = 0, arg 1 = pinCanon or pinVaccum, arg2 = On or OFF
#controll the servo:
#   order_id = 1, arg1 = True (open) or False (close)
#controll the led band:
#   order_id = 2

def sendOrderActuator(connToactuProcess, pinPWM, state): #state = 0 or 1
    dataToSend = [0, pinPWM, state]
    connToactuProcess.send(dataToSend)



def onVAccum(connToactuProcess):
    sendOrderActuator(connToactuProcess, pinVaccum, ON)

def offVAccum(connToactuProcess):
    sendOrderActuator(connToactuProcess, pinVaccum, OFF)

def onCanon(connToactuProcess):
    sendOrderActuator(connToactuProcess, pinCanon, ON)

def offCanon(connToactuProcess):
    sendOrderActuator(connToactuProcess, pinCanon, OFF)


def ledActivate(connToactuProcess):
    connToactuProcess.send([2])

def servoOpen(connToactuProcess):
    connToactuProcess.send([1, True])

def servoClose(connToactuProcess):
    connToactuProcess.send([1, False])