import time
from hardware import arduino, esp32

def process_action(action):
    print("Processing action: ", action)
    if action["name"] == "sleep":
        time.sleep(action["args"]["ms"] / 1000)
    if action["name"] == "startMove":
        esp32.start_move(action["args"]["motor"], action["args"]["time"])
    if action["name"] == "setTargetSpeed":
        esp32.set_target_speed(action["args"]["motor"], action["args"]["speed"])
    if action["name"] == "setArmMotorPosition":
        arduino.SetArmMotorPositionValue(action["args"]["value"])
    if action["name"] == "resetArmMotorPosition":
        arduino.ResetArmMotorPosition()
    if action["name"] == "openClaw":
        arduino.OpenClaw()
    if action["name"] == "closeClaw": 
        arduino.CloseClaw()
        

def process_actions(actions):
    for action in actions:
        process_action(action)
        time.sleep(0.03)
        print(esp32_serial.read_all())