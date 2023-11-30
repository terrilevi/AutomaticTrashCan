#!/usr/bin/python
import RPi.GPIO as GPIO
import time
from picamera2 import Picamera2
import os
import requests
import base64
import json


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


# Función para realizar la llamada a la API
def call_api(image_path):
    # Encodificación de la imagen a base64
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    base64_image = encode_image(image_path)

    # Configuración de los headers y payload para la API
    api_key = "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"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    prompt_text = (
        "Examine the image provided and categorize the visible waste item(s). Use these guidelines: "
        "1 for Organic Waste, 2 for Non-Recyclable Waste, and 3 for Recyclable Waste. "
        "If multiple different items are visible, categorize as Non-Recyclable (2). "
        "If all items are of the same type, categorize them into their appropriate bin. "
        "In cases of uncertainty or non-identifiable items, also categorize as Non-Recyclable (2).\n\n"
        "Respond ONLY with the number of the bin where the items should be placed, without any additional text. "
        "For example, respond with '1', '2', or '3' based on the categorization.\n\n"
        "This format is critical for the automation process in the waste sorting system."
        
    )


    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    response_data = response.json()
    content = response_data["choices"][0]["message"]["content"]
    bin_num = int(content)
    return bin_num

#############################CODE OF MOVING TWO L SERVOS ##################

from gpiozero import Servo
from time import sleep
import RPi.GPIO as GPIO

# Initialize the servos
servo2_1 = Servo(23, min_pulse_width=0.0005, max_pulse_width=0.0025)
servo2_2 = Servo(24, min_pulse_width=0.0005, max_pulse_width=0.0025)

# Dictionary mapping angles to servo values
angle_to_servo_value = {
    160: 0.56,  # Value for left (160 degrees)
    90: 0,      # Value for center (90 degrees)
    20: -0.53   # Value for right (20 degrees)
}

def move_servos_to_angle(angle):
    if angle in angle_to_servo_value:
        servo_value = angle_to_servo_value[angle]
        servo2_1.value = servo_value
        servo2_2.value = servo_value
    else:
        print("Angle not defined")

def perform_action(angle):
    move_servos_to_angle(angle)
    sleep(2)
    #move_servos_to_angle(90)
    servo2_1.detach()
    servo2_2.detach()

###########################CODE FOR HIGH SERVOSSSS####################

# Initialize both servos with their respective GPIO pins and pulse widths
servo1_1 = Servo(27, min_pulse_width=0.0005, max_pulse_width=0.0025)
servo1_2 = Servo(22, min_pulse_width=0.0005, max_pulse_width=0.0025)

# Dictionary mapping angles to servo values for each servo
angle_to_servo_value_servo1 = {
    160: 0.56,  # Adjust this value for 160 degrees for servo1
    90: 0       # Value for 90 degrees for servo1
}

angle_to_servo_value_servo2 = {
    160: -0.12,  # Adjust this value for 160 degrees for servo2
    90: 0.6      # Value for 90 degrees for servo2
}

def move_servos_and_detach(angle):
    """Moves both servos to a given angle and then detaches them."""
    servo1_1.value = angle_to_servo_value_servo1.get(angle, 0)
    servo1_2.value = angle_to_servo_value_servo2.get(angle, 0)
    sleep(1)
    servo1_1.detach()
    servo1_2.detach()


###################MAIN LOOP#############################
# GPIO setup for ultrasonic sensor
GPIO.setmode(GPIO.BOARD)
PIN_TRIGGER = 7
PIN_ECHO = 11
GPIO.setup(PIN_TRIGGER, GPIO.OUT)
GPIO.setup(PIN_ECHO, GPIO.IN)
GPIO.output(PIN_TRIGGER, GPIO.LOW)

print("System Initializing")
time.sleep(2)



# Main loop
try:
    CLOSE_THRESHOLD = 10  # Distance in cm, adjust as needed

    while True:
        # Trigger ultrasonic module
        GPIO.output(PIN_TRIGGER, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(PIN_TRIGGER, GPIO.LOW)

        # Measure pulse
        while GPIO.input(PIN_ECHO) == 0:
            pulse_start_time = time.time()
        while GPIO.input(PIN_ECHO) == 1:
            pulse_end_time = time.time()

        # Calculate distance
        pulse_duration = pulse_end_time - pulse_start_time
        distance = round(pulse_duration * 17150, 2)
        print(f"Distance: {distance} cm")

        # Check if object is within close range and capture image
        if distance < CLOSE_THRESHOLD:
            try:
                capture_image()
                image_path = "/home/pumtacho/Documents/pumtacho/images/photo.jpg"
                bin_num = call_api(image_path)
                print(f"Bin Number: {bin_num}")

                if bin_num in [1, 2, 3]:
                    perform_action(160 if bin_num == 1 else 90 if bin_num == 2 else 20)
                    sleep(1)
                    move_servos_and_detach(90)
                    sleep(1)
                    move_servos_and_detach(160)
                else:
                    print("Invalid response from API")
            except Exception as e:
                print(f"An error occurred: {e}")

        time.sleep(1)  # Delay to avoid excessive readings

except KeyboardInterrupt:
    print("Program terminated by user")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    GPIO.cleanup()
