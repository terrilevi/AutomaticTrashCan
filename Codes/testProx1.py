#!/usr/bin/python
import RPi.GPIO as GPIO
import time

# GPIO setup
GPIO.setmode(GPIO.BOARD)
PIN_TRIGGER = 7
PIN_ECHO = 11
GPIO.setup(PIN_TRIGGER, GPIO.OUT)
GPIO.setup(PIN_ECHO, GPIO.IN)
GPIO.output(PIN_TRIGGER, GPIO.LOW)

print("Testing Ultrasonic Sensor")
time.sleep(2)

try:
    while True:
        # Trigger ultrasonic module
        GPIO.output(PIN_TRIGGER, GPIO.HIGH)
        time.sleep(0.0000001)#agregue 2 ceros mas
        GPIO.output(PIN_TRIGGER, GPIO.LOW)

        # Measure pulse
        while GPIO.input(PIN_ECHO) == 0:
            pulse_start_time = time.time()
        while GPIO.input(PIN_ECHO) == 1:
            pulse_end_time = time.time()

        # Calculate distance
        pulse_duration = pulse_end_time - pulse_start_time
        distance = round(pulse_duration * 17150, 2)
        print("Measured Distance:", distance, "cm")

        time.sleep(1)

finally:
    GPIO.cleanup()
