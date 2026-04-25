import serial
import dotenv

arduino_serial = serial.Serial("/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_34330303436351E080E1-if00", 115200)


def ResetArmMotorPosition():
    global arduino_serial
    arduino_serial.write(bytes([0x10]))

def SetArmMotorPositionValue(pos):
    global arduino_serial
    high = (pos>> 8) & 0xFF;
    low = pos & 0xFF;

    arduino_serial.write(bytes([0x30, high, low]))
    
def OpenClaw():
    global arduino_serial
    arduino_serial.write(bytes([0x21]))

def CloseClaw():
    global arduino_serial
    arduino_serial.write(bytes([0x22]))

def SetClawAngle(angle):
    global arduino_serial
    arduino_serial.write(bytes([0x40, angle]))

def SetDisplayText(text):
    global arduino_serial
    """Send task code text to display (e.g., '123+321' or '213+132')"""
    arduino_serial.write(bytes([0x50]))  # Command byte for SetDisplayText
    # Send each character followed by null terminator
    for char in text:
        arduino_serial.write(bytes([ord(char)]))
    arduino_serial.write(bytes([0]))  # Null terminator