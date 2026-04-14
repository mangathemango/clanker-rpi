import time
from hardware import arduino, esp32

def process_action(action):
    if action["name"] == "sleep":
        print("sleeping")
        time.sleep(action["args"]["ms"] / 1000)
    if action["name"] == "startMove":
        print("startmoving")
        esp32.start_move(action["args"]["motor"], action["args"]["time"])
    if action["name"] == "setTargetSpeed":
        pass
    if action["name"] == "setArmMotorPosition":
        pass
    if action["name"] == "setArmMotorPositionUp":
        pass

def process_actions(actions):
    for action in actions:
        process_action(action)