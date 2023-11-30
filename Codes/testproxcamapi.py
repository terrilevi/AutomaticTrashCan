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
    CLOSE_THRESHOLD = 10  # distance in cm, adjust as needed
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
        print("Distance:", distance, "cm")

        # Check if object is within close range and capture image
        if distance < CLOSE_THRESHOLD:
            capture_image()
            call_api("/home/pumtacho/Documents/pumtacho/images/photo.jpg")
        time.sleep(1)  # Delay to avoid excessive readings

finally:
    GPIO.cleanup()
