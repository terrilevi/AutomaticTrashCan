from gpiozero import Servo
from time import sleep

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

# Start by moving both servos to 160 degrees
move_servos_and_detach(160)

while True:
    user_input = input("Enter 1 to open the trash can (move to 90 degrees), or any other key to quit: ")
    if user_input == '1':
        move_servos_and_detach(90)   # Move both to 90 degrees
        sleep(1)                     # Time for trash to drop
        move_servos_and_detach(160)  # Return both to 160 degrees
    else:
        break
