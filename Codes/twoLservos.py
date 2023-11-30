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

while True:
    user_input = input("Enter 1 (left), 2 (center), 3 (right), or 0 to exit: ")
    if user_input == '1':
        perform_action(160)
    elif user_input == '2':
        perform_action(90)
    elif user_input == '3':
        perform_action(20)
    elif user_input == '0':
        break
    else:
        print("Invalid input")
