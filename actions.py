import time
from hardware import arduino, esp32
from hardware.esp32 import esp32_serial
# from hardware.arduino import arduino_serial
arduino_serial = None
import serial
import dotenv
# from cv.qr_read import qr_data
import cv2
from pyzbar.pyzbar import decode
from cv.vision_place import get_chosen_circle_color_and_position

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

def qr_read():
    string_instruction = qr_read.qr_data()

def callibration_at_qr():
    

    while(string_instruction == None ):
        string_instruction = qr_read.qr_data()
        move_left()
        string_instruction = qr_read.qr_data()
        move_right()

def callibration_at_mat():
    pass


def execute_config():
    """Execute the config sequence with direct function calls (same as grabbing)"""
    execute_grabbing()  # Since config.json has the same actionQueue as grabbing.json

def move_motor(motor, speed, time_ds):
    if speed < 0:
        speed = (speed * -1) + 100
    esp32.set_target_speed(motor, speed)
    esp32.start_move(motor, time_ds)


def move_forward(time_ds, speed=100):
    move_motor(0, speed, time_ds)
    move_motor(3, speed, time_ds)
    move_motor(1, speed, time_ds)
    move_motor(2, speed, time_ds)
    time.sleep(time_ds / 10)

def move_backward(time_ds, speed=100):
    move_motor(0, -speed, time_ds)
    move_motor(3, -speed, time_ds)
    move_motor(1, -speed, time_ds)
    move_motor(2, -speed, time_ds)
    time.sleep(time_ds / 10)

def move_diagonal24(speed, time_ds):
    move_motor(1, speed, time_ds)
    move_motor(3, speed, time_ds)
    time.sleep(time_ds / 10)

def move_diagonal13(speed, time_ds):
    move_motor(0, int(speed * 0.9), time_ds)
    move_motor(2, int(speed * 0.9), time_ds)
    time.sleep(time_ds / 10)

def rotate_center(speed ,time_ds):
    move_motor(0, speed, time_ds)
    move_motor(1, speed, time_ds)
    move_motor(2, -speed, time_ds)
    move_motor(3, -speed, time_ds)
    time.sleep(time_ds / 10)

def move_right(time_ds, speed):
    move_motor(0, -speed, time_ds)
    move_motor(1, speed, time_ds)
    move_motor(2, -speed, time_ds)
    move_motor(3, speed, time_ds)
    

def put_material_above(index):
    angle = 0
    if index == 1:
        angle = 89
    if index == 2:
        angle = 100
    if index == 3:
        angle = 113
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
    esp32.set_angle(54)
    time.sleep(1)
    arduino.SetArmMotorPositionValue(2000)
    time.sleep(6)
    arduino.OpenClaw()
    time.sleep(1)
    arduino.SetArmMotorPositionValue(2400)
    time.sleep(5)
    arduino.CloseClaw()






def read_qr_code(cap=None):
    if cap is None:
        cap = cv2.VideoCapture(0)

    print("QR is scanning...")

    Data = None;


    ret, img = cap.read()

    print("ret", ret)


    qr_codes = decode(img)

    if qr_codes:
        Data = qr_codes[0].data.decode("utf-8")




    cap.release()

    print(Data)
    return Data

def initialise():
    arduino.ResetArmMotorPosition()
    time.sleep(6)
    arduino.OpenClaw()
    esp32.set_angle(100)
    time.sleep(1)



def main_path():
    initialise()

def flag_1():
    esp32.set_angle(56)
    time.sleep(1)
    # #Flag 1
    move_diagonal24(100, 18)
    move_forward(11)
    esp32.set_angle(129)
    # arduino.SetArmMotorPositionValue(1000)
    time.sleep(4)
    read_qr_code()
    # arduino.ResetArmMotorPosition()
    time.sleep(2)
    esp32.set_angle(56)
    time.sleep(1)
    move_diagonal13(100, 13)
    time.sleep(1)
    rotate_center(-100,2)
    time.sleep(1)
    move_forward(17)
    time.sleep(2)

def flag_2():
    esp32.set_angle(56)
    time.sleep(1)
    # # #Flag 2
    move_backward(11)
    time.sleep(1)
    time.sleep(1)
    rotate_center(77,10)
    time.sleep(1)
    move_forward(40)
    time.sleep(1)
    rotate_center(-80,10)
    time.sleep(2)
    esp32.set_angle(0)
    time.sleep(2)

def flag_3():
    calibrate_at_temp_zone(target_color="GREEN")
    esp32.set_angle(56)
    time.sleep(1)
    # #Flag 3
    move_forward(21)
    time.sleep(1)
    rotate_center(-75,10)
    move_forward(23)
    time.sleep(2)
    esp32.set_angle(0)

def flag_4():
    # # # #Flag 4
    move_forward(24)
    time.sleep(1)
    rotate_center(80,11)
    time.sleep(1)
    move_backward(14)
    time.sleep(1)

def flag_5():
    #Flag 5
    move_backward(11)
    time.sleep(1)
    rotate_center(80,11)
    time.sleep(1)
    move_forward(45)
    time.sleep(1)
    rotate_center(-80,11)
    time.sleep(2)

def flag_6():
    # #Flag 6
    move_forward(21)
    time.sleep(1)
    rotate_center(-80,10)
    move_forward(23)
    time.sleep(2)

def flag_7():
    #Flag 7
    move_forward(25)
    time.sleep(1)
    rotate_center(80,11)
    time.sleep(1)
    move_backward(14)
    time.sleep(1)

def flag_8():
    #Flag 8
    time.sleep(1)
    rotate_center(-80,18)
    move_forward(31)
    time.sleep(2)
    move_diagonal24(100, 16)
    time.sleep(2)


def set_angle(angle):
    global esp32_serial
    #0xFF, 1, 0(servo_id), 0(set_angle), angle_arg
    esp32_serial.write(bytes([0xFF, 1, 0, 0, angle]))


def test():
    arduino.OpenClaw()
    time.sleep(1)
    arduino.CloseClaw()
    time.sleep(1)
    arduino.SetArmMotorPositionValue(1200)
    time.sleep(1)
    arduino.SetArmMotorPositionValue(1320)
    time.sleep(1)
    rotate_center(100,5)
    rotate_center(-100,5)
    time.sleep(1)
    set_angle(180)
    time.sleep(1)
    set_angle(0)
    pass

def reset_serials():
    print("Resetting serials...")
    global esp32_serial, arduino_serial
    # esp32_serial.close()
    # arduino_serial.close()
    # time.sleep(2)
    esp32_serial = serial.Serial(dotenv.get_key(".env", "ESP32_PORT"), 115200)
    arduino_serial = serial.Serial(dotenv.get_key(".env", "ARDUINO_PORT"), 115200)
    time.sleep(1)
    print("Testing esp32_serial")
    print(esp32_serial.read_all())
    esp32_serial.write(bytes([]))
    print("Testing arduino_serial")
    print(arduino_serial.read_all())
    arduino_serial.write(bytes([]))




def calculate_dynamic_speed(distance, min_speed=50, max_speed=100, deadzone=5):
    """
    Calculate speed based on distance from target.
    Closer distance = slower speed, farther = faster speed
    """
    if distance < deadzone:
        return min_speed
    if distance > 100:
        return max_speed
    # Linear interpolation between min and max speed based on distance
    speed = min_speed + (distance - deadzone) / (100 - deadzone) * (max_speed - min_speed)
    return int(speed)


def calibrate_place_zone_step(current_position, target_position = (344.6, 273.0), color="GREEN"):
    current_x, current_y = current_position
    target_x, target_y = target_position
    diff_x = current_x - target_x
    diff_y = current_y - target_y

    y_threshold = 10
    x_threshold = 10

    print(f"Diff X: {diff_x}, Diff Y: {diff_y}")

    # Calculate distances for dynamic speed
    dist_y = abs(diff_y)
    dist_x = abs(diff_x)
    
    if diff_y < -y_threshold or diff_y > y_threshold:
        if abs(diff_x) > abs(diff_y):
            speed_x = calculate_dynamic_speed(dist_x, min_speed=30, max_speed=60, deadzone=5)
            direction_x = 1 if diff_x > 0 else -1
            if direction_x > 0:
                move_forward(4, speed=speed_x)
            else:
                move_backward(4, speed=speed_x)
            return False
        speed_y = calculate_dynamic_speed(dist_y, min_speed=60, max_speed=75, deadzone=5)
        direction_y = -1 if diff_y < 0 else 1
        move_diagonal13(direction_y * speed_y, 9)
        return False
    
    print("Y axis calibration complete")
    if diff_x < -x_threshold or diff_x > x_threshold:
        speed_x = calculate_dynamic_speed(dist_x, min_speed=30, max_speed=60, deadzone=5)
        direction_x = 1 if diff_x > 0 else -1
        if direction_x > 0:
            move_forward(4, speed=speed_x)
        else:
            move_backward(4, speed=speed_x)
        return False
    print("X axis calibration complete")
    return True

def calibrate_at_temp_zone(target_color="GREEN", cap=None):
    color_position = {
        "RED": 500,
        "GREEN": 0,
        "BLUE": -500
    }
    if cap is None:
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    for i in range(20):
        output = get_chosen_circle_color_and_position(cap=cap)
        if output == True:
            break
        print(output)

        color, position = output
        if position == None or color == "NONE":
            print("No position found")
            position = (500,-500, 0)
            color = target_color
        x,y,_ = position
        if color != "UNKNOWN":
            x += color_position[target_color] - color_position[color]
        if calibrate_place_zone_step((x,y)):
            break
        time.sleep(0.4)


def put_material(index):
    angle = 0
    if index == 1:
        angle = 89
    if index == 2:
        angle = 100
    if index == 3:
        angle = 113
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
    esp32.set_angle(54)
    time.sleep(1)
    arduino.SetArmMotorPositionValue(480)
    time.sleep(6)
    arduino.OpenClaw()
    time.sleep(1)
    arduino.SetArmMotorPositionValue(2400)
    time.sleep(5)
    arduino.CloseClaw()

def main():
    arduino.SetClawAngle(140)


    # flag_1()
    # flag_2()

    # calibrate_at_temp_zone(target_color="GREEN")
    # calibrate_at_temp_zone(target_color="RED")
    # calibrate_at_temp_zone(target_color="BLUE")
    # flag_3()
    # calibrate_at_temp_zone(target_color="GREEN")
    # calibrate_at_temp_zone(target_color="RED")
    # calibrate_at_temp_zone(target_color="BLUE")
    pass

