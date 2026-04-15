import time
from hardware import arduino, esp32
from hardware.esp32 import esp32_serial

def process_action(action):
    print("Processing action: ", action)
    if action["name"] == "sleep":
        time.sleep(action["args"]["ms"] / 1000)
    if action["name"] == "startMove":
        esp32.start_move(action["args"]["motor"], action["args"]["time"])
    if action["name"] == "setTargetSpeed":
        esp32.set_target_speed(action["args"]["motor"], action["args"]["speed"])
        pass
    if action["name"] == "setArmMotorPosition":
        pass
    if action["name"] == "setArmMotorPositionUp":
        pass

def process_actions(actions):
    for action in actions:
        process_action(action)
        time.sleep(0.03)
        print(esp32_serial.read_all())