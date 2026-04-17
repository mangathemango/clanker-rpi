import time
from hardware import arduino, esp32
from hardware.esp32 import esp32_serial
# from cv.qr_read import qr_data
import cv2

def grabProp():
    # Placeholder for grab prop action - define as needed
    print("Executing grabProp")

def execute_putting():
    import time
    """Execute the putting sequence with direct function calls"""
    # grabProp()
    arduino.ResetArmMotorPosition()
    esp32.set_angle(178)
    time.sleep(7)
    arduino.SetArmMotorPositionValue(1000)
    time.sleep(2)
    arduino.CloseClaw()
    time.sleep(2)
    esp32.set_angle(20)

def execute_grabbing():
    import time
    """Execute the grabbing sequence with direct function calls"""
    grabProp()
    arduino.OpenClaw()
    arduino.ResetArmMotorPosition()
    # esp32.set_angle(20)
    time.sleep(2)
    arduino.SetArmMotorPositionValue(2290)
    time.sleep(2)
    arduino.CloseClaw()
    time.sleep(2)
    arduino.SetArmMotorPositionValue(2400)
    time.sleep(2)
    # esp32.set_angle(178)
    time.sleep(2)
    arduino.SetArmMotorPositionValue(1800)
    time.sleep(2)
    arduino.OpenClaw()

def execute_config():
    """Execute the config sequence with direct function calls (same as grabbing)"""
    execute_grabbing()  # Since config.json has the same actionQueue as grabbing.json

def move_motor(motor, speed, time_ds):
    if speed < 0:
        speed = (speed * -1) + 100
    esp32.set_target_speed(motor, speed)
    esp32.start_move(motor, time_ds)

def move_forward(time_ds):
    move_motor(0, 100, time_ds)
    move_motor(3, 100, time_ds)
    move_motor(1, 100, time_ds)
    move_motor(2, 100, time_ds)
    time.sleep(time_ds / 10)

def move_backward(time_ds):
    move_motor(2, -100, time_ds)
    move_motor(1, -100, time_ds)
    move_motor(3, -100, time_ds)
    move_motor(0, -100, time_ds)
    time.sleep(time_ds / 10)

def move_diagonal(speed, time_ds):
    move_motor(1, speed, time_ds)
    move_motor(3, speed, time_ds)
    time.sleep(time_ds / 10)

def rotate_center(time_ds):
    move_motor(0, 100, time_ds)
    move_motor(1, 100, time_ds)
    move_motor(2, -100, time_ds)
    move_motor(3, -100, time_ds)

def move_right(time_ds):
    move_motor(0, 100, time_ds)
    move_motor(1, -100, time_ds)
    move_motor(2, 100, time_ds)
    move_motor(3, -100, time_ds)
    

def put_material(index):
    angle = 0
    if index == 1:
        angle = 93
    arduino.OpenClaw()
    esp32.set_angle(angle)
    arduino.OpenClaw()
    time.sleep(1)
    arduino.SetArmMotorPositionValue(1800)
    time.sleep(3)
    arduino.CloseClaw()
    time.sleep(1)
    arduino.SetArmMotorPositionValue(2400)
    time.sleep(3)
    esp32.set_angle(40)
    time.sleep(1)
    arduino.SetArmMotorPositionValue(480)
    time.sleep(6)
    arduino.OpenClaw()
    time.sleep(1)
    arduino.SetArmMotorPositionValue(2400)
    time.sleep(5)
    arduino.CloseClaw()



def main_path():
    # move_diagonal(100, 15)
    # move_forward(10)
    # arduino.SetArmMotorPositionValue(1000)
    # time.sleep(3)
    # print(qr_data())
    # move_forward(20)
    # time.sleep(5)
    arduino.CloseClaw()
    arduino.SetArmMotorPositionValue(2000)
    time.sleep(5)
    arduino.OpenClaw()
    time.sleep(1)
    arduino.SetArmMotorPositionValue(2400)
    # move_right(10)

def read_qr_code():
    esp32.set_angle(150)

def main():
    read_qr_code()

    