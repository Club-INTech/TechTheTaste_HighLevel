from multiprocessing import Pipe

OFF = 0
ON = 1

pinCanon = 12
pinVaccum = 16

def sendOrderActuator(connToactuProcess, pinPWM, state): #state = 0 or 1
    dataToSend = [pinPWM, state]
    connToactuProcess.send(dataToSend)


class actuar
def onVAccum(connToactuProcess):
    sendOrderActuator(connToactuProcess, pinVaccum, ON)

def offVAccum(connToactuProcess):
    sendOrderActuator(connToactuProcess, pinVaccum, OFF)

def onCanon(connToactuProcess):
    sendOrderActuator(connToactuProcess, pinCanon, ON)

def offCanon(connToactuProcess):
    sendOrderActuator(connToactuProcess, pinCanon, OFF)
