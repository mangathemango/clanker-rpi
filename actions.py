import time
import math
from hardware import arduino, esp32
from hardware.esp32 import esp32_serial
from hardware.arduino import arduino_serial
arduino_serial = None
import cv2
from pyzbar.pyzbar import decode
from cv.vision_place import get_chosen_circle_color_and_position
from cv.line_guard import get_line_guard_state
from pprint import pprint
def set_angle(degree):
    esp32.set_angle(degree)
import numpy as np
from cv.line_guard import get_line_guard_state

def move_motor(motor, speed, time_ds):
    if speed < 0:
        speed = (speed * -1) + 100
    esp32.set_target_speed(motor, speed)
    esp32.start_move(motor, time_ds)


def move_forward(speed, time_ds, delay=True):
    move_motor(0, speed, time_ds)
    move_motor(3, speed, time_ds)
    move_motor(1, speed, time_ds)
    move_motor(2, speed, time_ds)
    if delay:
        time.sleep(time_ds / 10)

def move_backward(speed, time_ds, delay=True):
    move_motor(0, -speed, time_ds)
    move_motor(3, -speed, time_ds)
    move_motor(1, -speed, time_ds)
    move_motor(2, -speed, time_ds)
    if delay:
        time.sleep(time_ds / 10)

def move_diagonal24(speed, time_ds, delay=True):
    move_motor(1, speed, time_ds)
    move_motor(3, speed, time_ds)
    if delay:
        time.sleep(time_ds / 10)

def move_diagonal13(speed, time_ds, delay=True):
    move_motor(0, int(speed * 0.9), time_ds)
    move_motor(2, int(speed * 0.9), time_ds)
    if delay:
        time.sleep(time_ds / 10)

def move_diagonal(forward_speed, sideway_speed, time_ds, delay=True):
    """sideway_speed note: left is negative, right is positive"""
    speed_0 = (forward_speed - sideway_speed) // 2
    speed_1 = (forward_speed + sideway_speed) // 2
    print(speed_0, speed_1)
    if speed_1 != 0:
        move_motor(1, speed_1, time_ds)
        move_motor(3, speed_1, time_ds)
    if speed_0 != 0:
        move_motor(0, speed_0, time_ds)
        move_motor(2, speed_0, time_ds)
    if delay:
        time.sleep(time_ds / 10)

def rotate_center(speed,time_ds, delay=True):
    move_motor(0, speed, time_ds)
    move_motor(1, speed, time_ds)
    move_motor(2, -speed, time_ds)
    move_motor(3, -speed, time_ds)
    if delay:
        time.sleep(time_ds / 10)

def move_right(speed, time_ds, delay=True):
    move_motor(0, -speed, time_ds)
    move_motor(1, speed, time_ds)
    move_motor(2, -speed, time_ds)
    move_motor(3, speed, time_ds)
    if delay:
        time.sleep(time_ds / 10)


def move_left(speed, time_ds, delay=True):
    move_motor(0, speed, time_ds)
    move_motor(1, -speed, time_ds)
    move_motor(2, speed, time_ds)
    move_motor(3, -speed, time_ds)
    if delay:
        time.sleep(time_ds / 10)


def calibrate_position(cap, color, target_angle, tolerance=1, rotation_speed=50, steps=-1):
    while steps != 0:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame")
            break
        angle, _, _ = get_line_guard_state(frame, color)
        diff = target_angle - angle
        if abs(diff) < tolerance:  # tolerance for angle matching
            break
        speed = rotation_speed if diff > 0 else -rotation_speed
        rotate_center(speed, 1)  # small rotation step
        steps -= 1


def read_qr_code(cap=None):
    release_flag = False
    if cap is None:
        release_flag = True
        cap = cv2.VideoCapture(0)

    print("QR is scanning...")

    data = None


    ret, img = cap.read()

    print("ret", ret)


    qr_codes = decode(img)

    if qr_codes:
        data = qr_codes[0].data.decode("utf-8")

    print(data)

    if release_flag:
        cap.release()
    return data

def initialise():
    arduino.ResetArmMotorPosition()
    time.sleep(6)
    arduino.OpenClaw()
    esp32.set_angle(100)
    time.sleep(1)




def flag_1():
    arduino.SetArmMotorPositionValue(1320)
    time.sleep(2)
    esp32.set_angle(57)
    time.sleep(1)
    # #Flag 1
    move_diagonal24(100, 17)
    move_forward(100, 13)
    read_qr_code()
    # return
    time.sleep(1)
    esp32.set_angle(127)
    move_diagonal13(100,10)
    time.sleep(1)
    calibrate_at_line("gray","upside_down", 240)
    move_forward(100, 17)

def flag_2():
    esp32.set_angle(57)
    time.sleep(1)
    # # #Flag 2
    move_backward(100, 11)
    time.sleep(1)
    time.sleep(1)
    rotate_center(77,10)
    time.sleep(1)
    move_forward(100, 40)
    time.sleep(1)
    rotate_center(-80,10)
    time.sleep(2)
    esp32.set_angle(0)
    time.sleep(2)

def flag_3():
    calibrate_at_temp_zone(target_color="GREEN")
    esp32.set_angle(57)
    time.sleep(1)
    # #Flag 3
    move_forward(100, 21)
    time.sleep(1)
    rotate_center(-75,10)
    move_forward(100, 23)
    time.sleep(2)
    esp32.set_angle(0)

def flag_4():
    # # # #Flag 4
    move_forward(100, 24)
    time.sleep(1)
    rotate_center(80,11)
    time.sleep(1)
    move_backward(100, 14)
    time.sleep(1)

def flag_5():
    #Flag 5
    move_backward(100, 11)
    time.sleep(1)
    rotate_center(80,11)
    time.sleep(1)
    move_forward(100, 45)
    time.sleep(1)
    rotate_center(-80,11)
    time.sleep(2)

def flag_6():
    # #Flag 6
    move_forward(100, 21)
    time.sleep(1)
    rotate_center(-80,10)
    move_forward(100, 23)
    time.sleep(2)

def flag_7():
    #Flag 7
    move_forward(100, 25)
    time.sleep(1)
    rotate_center(80,11)
    time.sleep(1)
    move_backward(100, 14)
    time.sleep(1)

def flag_8():
    #Flag 8
    time.sleep(1)
    rotate_center(-80,18)
    move_forward(100, 31)
    time.sleep(2)
    move_diagonal24(100, 16)
    time.sleep(2)



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


def calibrate_place_zone_step(current_position, target_position=(320, 273.0), color="GREEN", tolerance=10, min_speed=30, max_speed=40, ideal_min=10, ideal_max=50, history_length=6):
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
                move_forward(speed_x, 4)
            else:
                move_backward(speed_x, 4)
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
            move_forward(speed_x, 4)
        else:
            move_backward(speed_x, 4)
        return False
    print("X axis calibration complete")
    return True

def calibrate_at_temp_zone(target_color="GREEN", cap=None, step=20, tolerance=10):
    color_position = {
        "RED": 500,
        "GREEN": 0,
        "BLUE": -500
    }
    if cap is None:
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    for _ in range(step):
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
        if calibrate_place_zone_step((x,y), tolerance = tolerance):
            break
        _, frame = cap.read()
        line_guard_state = get_line_guard_state(frame, color="gray")
        angle, _, _ = line_guard_state
        pprint(angle)
        if angle < 30 and  angle > 5:
            rotate_center(100,1)
        if angle > 70 or angle < -5:
            rotate_center(-100,1)
        time.sleep(0.2)

def calibrate_at_line(color="yellow", orientation="straight", center=240, angle_tolerance=0.5, tolerance_px=85, cap=None, max_iters=20, move_speed=80):
    if cap is None:
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    frame_center_y = center


    for i in range(max_iters):
        flag_position = 0
        flag_angle = 0
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame")
            break

        angle, pixels, boundary = get_line_guard_state(frame, color, orientation)

        if boundary.y1 is None:
            print("No line found")
            time.sleep(0.2)
            continue

        time.sleep(1)
        avg_y = (boundary.y1 + boundary.y2) / 2
        error = avg_y - frame_center_y

        print(f"Line center error: {error:.1f}px, angle: {angle:.1f}")

        if abs(error) <= tolerance_px and flag_position != 1:
            print("Line is centered in the frame")
            flag_position = 1
        elif error > 0 and flag_position != 1:
            print("Line is right of center, moving right")
            move_right(move_speed, 5)
        elif error < 0 and flag_position != 1:
            print("Line is left of center, moving left")
            move_left(move_speed, 5)
        
        angle, pixels, boundary = get_line_guard_state(frame, color, orientation)

        if boundary.y1 is None:
            print("No line found")
            time.sleep(0.2)
            continue

        time.sleep(1)
        avg_y = (boundary.y1 + boundary.y2) / 2
        error = avg_y - frame_center_y

        print(f"Line center error: {error:.1f}px, angle: {angle:.1f}")
        if abs(angle) <= angle_tolerance:
            print("angle aligned")
            flag_angle = 1
        elif angle > 0:
            rotate_center(-60,2)
        else:
            rotate_center(60,2)

        if flag_angle and flag_position == 1:
            print("calibration complete")
            break

        time.sleep(0.2)

def calibrate_angle(color="yellow", orientation="straight", center=240, angle_tolerance=0.5, cap=None, max_iters=20, move_speed=80):
    if cap is None:
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    frame_center_y = center

    for i in range(max_iters):
        flag_position = 0
        flag_angle = 0
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame")
            break
        
        angle, pixels, boundary = get_line_guard_state(frame, color, orientation)

        if boundary.y1 is None:
            print("No line found")
            time.sleep(0.2)
            continue

        time.sleep(1)
        avg_y = (boundary.y1 + boundary.y2) / 2
        error = avg_y - frame_center_y

        print(f"Line center error: {error:.1f}px, angle: {angle:.1f}")
        if abs(angle) <= angle_tolerance:
            print("angle aligned")
            break
        elif angle > 0:
            rotate_center(-60,2)
        else:
            rotate_center(60,2)

        time.sleep(0.2)

def calibrate_distance(color="yellow", orientation="straight", center=240, tolerance_px=85, cap=None, max_iters=20, move_speed=80):
    if cap is None:
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    frame_center_y = center


    for i in range(max_iters):
        flag_position = 0
        flag_angle = 0
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame")
            break

        angle, pixels, boundary = get_line_guard_state(frame, color, orientation)

        if boundary.y1 is None:
            print("No line found")
            time.sleep(0.2)
            continue

        time.sleep(1)
        avg_y = (boundary.y1 + boundary.y2) / 2
        error = avg_y - frame_center_y

        print(f"Line center error: {error:.1f}px, angle: {angle:.1f}")

        if abs(error) <= tolerance_px and flag_position != 1:
            print("Line is centered in the frame")
            break
        elif error > 0 and flag_position != 1:
            print("Line is right of center, moving right")
            move_right(move_speed, 5)
        elif error < 0 and flag_position != 1:
            print("Line is left of center, moving left")
            move_left(move_speed, 5)

        time.sleep(0.2)

def main_path():
    initialise()

def soft_open_claw():
    arduino.SetClawAngle(80)

def close_claw():
    arduino.SetClawAngle(165)

def pick_material_from_storage_1():
    soft_open_claw()
    esp32.set_angle(39)
    time.sleep(2)
    arduino.SetArmMotorPositionValue(1050)
    time.sleep(1)
    esp32.set_angle(43)
    time.sleep(1)
    close_claw()
    time.sleep(1)
    arduino.SetArmMotorPositionValue(1320)
    time.sleep(3)

def pick_material_from_storage_2():
    soft_open_claw()
    esp32.set_angle(51)
    time.sleep(2)
    arduino.SetArmMotorPositionValue(1050)
    time.sleep(1)
    esp32.set_angle(53)
    time.sleep(1)
    close_claw()
    time.sleep(1)
    arduino.SetArmMotorPositionValue(1320)
    time.sleep(3)

def pick_material_from_storage_3():
    soft_open_claw()
    esp32.set_angle(67)
    time.sleep(2)
    arduino.SetArmMotorPositionValue(1100)
    time.sleep(1)
    close_claw()
    time.sleep(1)
    arduino.SetArmMotorPositionValue(1320)
    time.sleep(3)

def put_material_into_storage_1():
    esp32.set_angle(44)
    close_claw()
    time.sleep(1)
    arduino.SetArmMotorPositionValue(1050)
    time.sleep(1)
    esp32.set_angle(39)
    soft_open_claw()
    time.sleep(1)
    arduino.SetArmMotorPositionValue(1320)
    time.sleep(3)

def place_material():
    esp32.set_angle(0)
    time.sleep(1)
    arduino.SetArmMotorPositionValue(300)
    time.sleep(3)
    arduino.OpenClaw()
    time.sleep(1)
    arduino.SetArmMotorPositionValue(1320)
    time.sleep(3)


def pick_up_material():
    arduino.OpenClaw()
    esp32.set_angle(0)
    arduino.SetArmMotorPositionValue(300)
    time.sleep(3)
    arduino.CloseClaw()
    time.sleep(1)
    arduino.SetArmMotorPositionValue(1320)

def do_temp_zone_routine():
    esp32.set_angle(0)
    calibrate_at_temp_zone(target_color="GREEN")
    pick_material_from_storage_1()
    place_material()
    calibrate_at_temp_zone(target_color="RED")
    pick_material_from_storage_2()
    place_material()
    calibrate_at_temp_zone(target_color="BLUE")
    pick_material_from_storage_3()
    place_material()

def main():
    # calibrate_at_line("yellow","straight", 240)
    # flag_1()
    esp32.set_angle(0)
    # return
    # arduino.ResetArmMotorPosition()

    # cap = cv2.VideoCapture(0)
    pass
