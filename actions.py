import time
from hardware import arduino, esp32

def grabProp():
    # Placeholder for grab prop action - define as needed
    print("Executing grabProp")

def execute_putting():
    """Execute the putting sequence with direct function calls"""
    grabProp()
    arduino.ResetArmMotorPosition()
    esp32.set_angle(178)
    time.sleep(7)
    arduino.SetArmMotorPositionValue(1000)
    time.sleep(2)
    arduino.CloseClaw()
    time.sleep(2)
    esp32.set_angle(20)

def execute_grabbing():
    """Execute the grabbing sequence with direct function calls"""
    grabProp()
    arduino.OpenClaw()
    arduino.ResetArmMotorPosition()
    esp32.set_angle(20)
    time.sleep(2)
    arduino.SetArmMotorPositionValue(2290)
    time.sleep(2)
    arduino.CloseClaw()
    time.sleep(2)
    arduino.SetArmMotorPositionValue(2400)
    time.sleep(2)
    esp32.set_angle(178)
    time.sleep(2)
    arduino.SetArmMotorPositionValue(1800)
    time.sleep(2)
    arduino.OpenClaw()

def execute_config():
    """Execute the config sequence with direct function calls (same as grabbing)"""
    execute_grabbing()  # Since config.json has the same actionQueue as grabbing.json