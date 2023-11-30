#!/usr/bin/python

#libraries braries
import RPi.GPIO as GPIO
import time

## to photograph and view the photo
import subprocess

## use to gpt
from flask import Flask, request
import base64
import requests
import json

# use to camera
from picamera2 import Picamera2
import os

def distance() -> float: 

    #GPIO Mode (BOARD / BCM)
    GPIO.setmode(GPIO.BCM)

    #set GPIO Pins
    GPIO_TRIGGER = 16
    GPIO_ECHO = 18

    #set GPIO direction (IN / OUT)
    GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
    GPIO.setup(GPIO_ECHO, GPIO.IN)
    ############

    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)

    # set Trigger after 0.01ms to LOW
    time.sleep(0.000001)
    GPIO.output(GPIO_TRIGGER, False)

    startTime = time.time()
    stopTime = time.time()

    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()

    # save time of arrival
    while (GPIO.input(GPIO_ECHO) == 1):
        StopTime = time.time()

    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2

    return distance
##################

def distance1(PIN_TRIGGER: int, PIN_ECHO: int)->float:
    '''
    Determinate distance
    '''
    try:
        GPIO.setmode(GPIO.BOARD)

        #   PIN_TRIGGER = 7
        #   PIN_ECHO = 11

        GPIO.setup(PIN_TRIGGER, GPIO.OUT)
        GPIO.setup(PIN_ECHO, GPIO.IN)

        GPIO.output(PIN_TRIGGER, GPIO.LOW)

        print("Waiting for sensor to settle")

        time.sleep(0.00001)

        print("Calculating distance")

        GPIO.output(PIN_TRIGGER, GPIO.HIGH)

        time.sleep(0.00001)

        GPIO.output(PIN_TRIGGER, GPIO.LOW)

        while GPIO.input(PIN_ECHO)==0:
            pulse_start_time = time.time()
        while GPIO.input(PIN_ECHO)==1:
            pulse_end_time = time.time()

        pulse_duration = pulse_end_time - pulse_start_time
        distance = round(pulse_duration * 17150, 2)
        # print("Distance:",distance,"cm")
        return (distance)

    finally:
        GPIO.cleanup()
###########
def capture_image():
    '''
    photography one photo
    '''
    ## The idea is to optimize the code

    # Ejecutar el comando libcamera-jpeg para capturar una imagen y guardarla como test.jpg

    image_directory = "/home/pumtacho/Documents/pumtacho/images"
    file_name = "photo.jpg"

    picam2.start()
    image_path = os.path.join(image_directory, file_name)
    picam2.capture_file(image_path)
    picam2.stop()
    print("Image captured and saved to", image_path)
#############
def promptGpt(image_path:str)-> str: ##image_path is the image captured
    '''
    image_path: It is directory of the photo, for example
    : /home/pumtacho/Documents/pumtacho/images/test.jpg
    Generate the query with the received image
    '''

    # image_path = "/home/moises/Documents/TestCamera/images/photo.jpg"
    if os.path.isfile(image_path):
        print("File exists.")
    else:
        print("File does not exist.")


    # OpenAI API Key
    api_key = "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"

    # Function to encode the image
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
        

    # Getting the base64 string
    base64_image = encode_image(image_path)

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
    return content #return a str
#############
def setAngle(angle: int, pin: int, pwm, Hz=50):
    '''
    sets the input angle and translates it to pwm pulse
    angle: rotation servomotor | pwm: pwm object | Hz: signal pwm
    '''
    try:
        duty = angle / 18 + 2
        # Activa el pin
        GPIO.output(pin, True)
        pwm.ChangeDutyCycle(duty)
        # Espera 1 segundo para que el servo tenga tiempo de girar
        time.sleep(1)
        # Desactiva el pin
        GPIO.output(pin, False)
        # Cambia el duty a 0 para que no se sigan enviando señales al servo
        pwm.ChangeDutyCycle(0)
    except Exception as e:
        print("An error occurred:", e)

#####################
def moveAngle(pin, option = '2'):
    '''
    Rotate the angle acording to the output of pgt
    '''
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    pwm = GPIO.PWM(pin, 50)
    pwm.start(0)


    try:
        # Llama a tu función con los parámetros deseados
        setAngle(45, pin, pwm)
        if (option == '1'):
            setAngle(45, pin, pwm)
        elif (option == '3'):
            setAngle(90, pin, pwm)
        else:
            setAngle(135, pin, pwm)
    finally:
        # Limpia los recursos GPIO al final del script
        pwm.stop()
        GPIO.cleanup()


###############

