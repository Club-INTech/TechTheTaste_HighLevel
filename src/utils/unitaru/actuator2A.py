import RPi.GPIO as GPIO


#activate motor to throw cherry
#power btwn 0 and 100
def trowCherry(power : int) :
    print("value not in good range") if ((power < 0) or (power > 100))
    GPIO.setmode(GPIO.BCM)
    motorPIN = 12
    
