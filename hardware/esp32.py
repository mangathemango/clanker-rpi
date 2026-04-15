import serial
import time
import dotenv

esp32_serial = serial.Serial(dotenv.get_key(".env", "ESP32_PORT"), 115200)

def set_target_speed(motor_id, speed):
    #0xFF 0 Motor_id 0 speed_arg
    esp32_serial.write(bytes([0xFF, 0, motor_id, 0, speed]))
    
def set_ramp_time(motor_id, time):
    #0xFF 0 Motor_id 1 time_arg
    esp32_serial.write(bytes([0xFF, 0, motor_id, 1, time]))
    
def start_move(motor_id, time):
    #0xFF 0 Motor_id 2 time_arg
    esp32_serial.write(bytes([0xFF, 0, motor_id, 2, time]))
    
def set_angle(angle):
    #0xFF, 1, 0(servo_id), 0(set_angle), angle_arg
    esp32_serial.write(bytes([0xFF, 1, 0, 0, angle]))

if __name__ == "__main__":
    try:
        set_target_speed(0, 100)
        time.sleep(0.3)
        print(esp32_serial.read_all())
        set_target_speed(1, 100)
        time.sleep(0.3)
        print(esp32_serial.read_all())
        set_target_speed(2, 100)
        time.sleep(0.3)
        print(esp32_serial.read_all())
        set_target_speed(3, 100)
        time.sleep(0.3)
        print(esp32_serial.read_all())
        start_move(0, 50)
        start_move(1, 50)
        start_move(3, 50)
        start_move(2, 50)
        time.sleep(0.3)
        print(esp32_serial.read_all())
    except: 
        pass
