# to servo
import RPi.GPIO as GPIO
import time


# make sure ti write


### call the functions of module.py
import module as mod
#########
#pins sensor
pinTriguer = 7
pinEcho = 11
#pins servo
pin_servo1_2 = 16
pin_servo3_4 = 18



# set the angle of the servo gateway
servo1_2 = 90
# set the angle of the servo direction
servo3_4 = 90


if __name__ == '__main__':
    try:
        while True:
            dist = mod.distance1(pinTriguer,pinEcho)
            print ("Measured Distance = %.1f cm" % dist)
            servo1_2 = mod.setAngle(90, pin_servo1_2, pwm = GPIO.PWM(pin_servo1_2, 50))

            if (dist < 10):
                imagePath = mod.encenderCam()
                query = mod.promptGpt(imagePath)
                #directions 
                servo3_4 = mod.moveAngle(pin_servo3_4, query)

                #gateways
                servo1_2 = mod.setAngle(90, pin_servo1_2, pwm = GPIO.PWM(pin_servo1_2, 50))
            time.sleep(1)
            

        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()