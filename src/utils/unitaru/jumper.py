import RPi.GPIO as GPIO 

RISING = 0
FALLING = 1

def waitingJumper(edge):
    EDGES = [ [True, False], [False, True]]
    EDGE = EDGES[edge] #select the edge

    GPIO.setmode(GPIO.BCM)
    jumper = 12 #digital Output

    GPIO.setup(jumper, GPIO.IN)
    ctn = True
    while ctn:
        ctn = EDGE[GPIO.input(jumper)]
        print("waiting jumper")

waitingJumper(RISING)



