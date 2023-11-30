#!/usr/bin/python
import RPi.GPIO as GPIO
import time
from picamera2 import Picamera2
import os

# Initialize and configure the camera outside the function
picam2 = Picamera2()
config = picam2.create_still_configuration()
picam2.configure(config)

# Function to capture an image
def capture_image():
    image_directory = "/home/pumtacho/Documents/pumtacho/images"
    file_name = "photo.jpg"

    picam2.start()
    image_path = os.path.join(image_directory, file_name)
    picam2.capture_file(image_path)
    picam2.stop()
    print("Image captured and saved to", image_path)

# GPIO setup for ultrasonic sensor
GPIO.setmode(GPIO.BOARD)
PIN_TRIGGER = 7
PIN_ECHO = 11
GPIO.setup(PIN_TRIGGER, GPIO.OUT)
GPIO.setup(PIN_ECHO, GPIO.IN)
GPIO.output(PIN_TRIGGER, GPIO.LOW)

print("System Initializing")
time.sleep(2)

# Function to measure distance
def measure_distance():
    # Trigger ultrasonic module
    GPIO.output(PIN_TRIGGER, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(PIN_TRIGGER, GPIO.LOW)

    # Measure pulse
    while GPIO.input(PIN_ECHO) == 0:
        pulse_start_time = time.time()
    while GPIO.input(PIN_ECHO) == 1:
        pulse_end_time = time.time()

    # Calculate and return distance
    pulse_duration = pulse_end_time - pulse_start_time
    return round(pulse_duration * 17150, 2)

# Main loop
try:
    CLOSE_THRESHOLD = 15  # distance in cm, adjust as needed

    # Initial distance measurement
    initial_distance = measure_distance()
    print("Initial Distance:", initial_distance, "cm")
    time.sleep(2)  # Waiting a bit before starting the main loop

    while True:
        distance = measure_distance()
        print("Distance:", distance, "cm")

        # Check if object is within close range and capture image
        if distance < CLOSE_THRESHOLD:
            capture_image()

        time.sleep(1)  # Delay to avoid excessive readings

finally:
    GPIO.cleanup()




