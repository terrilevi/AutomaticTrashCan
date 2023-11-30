#!/usr/bin/python
import RPi.GPIO as GPIO
from picamera2 import Picamera2
import os
import requests
import base64
import json

#servos 
from gpiozero import Servo
from time import sleep

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
        "Analyze the image provided and identify each visible waste item. "
        "Categorize the items based on the following rules: "
        "If the image contains multiple different types of items, categorize them collectively under Non-Recyclable Waste Bin (2). "
        "If all items are of the same type, categorize them into their appropriate bin. "
        "For uncertain or non-identifiable items, use Non-Recyclable Waste Bin (2).\n\n"
        "Respond with the bin number, followed by a colon and a space, and then list the identified items. "
        "Ensure the response always starts with the bin number. For example:\n"
        "2: Banana, Plastic Water Bottle, Paper Napkin\n"
        "1: Apple\n"
        "3: Plastic Bottle\n"
        "2: NotSure\n\n"
        "This format is crucial for the automated process that sorts the waste based on your categorization."
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
    print(content)

def setServoHigh():

    #define global variables 
    global servo1_1, servo1_2, angle_to_servo_value_servo1, angle_to_servo_value_servo2
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

def move_servos_and_detach(angle:int):
    """Moves both directions servos to a given angle and then detaches them."""
    servo1_1.value = angle_to_servo_value_servo1.get(angle, 0)
    servo1_2.value = angle_to_servo_value_servo2.get(angle, 0)
    sleep(1)
    servo1_1.detach()
    servo1_2.detach()

def moveHighServo(estado:str):
    '''
    Open gate
    '''
    if estado == '1':
        move_servos_and_detach(90)   # Move both to 90 degrees
        sleep(1)                     # Time for trash to drop
        move_servos_and_detach(160)  # Return both to 160 degrees
#################
# twoLservo
  