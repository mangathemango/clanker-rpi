import serial
import dotenv

arduino_serial = serial.Serial(dotenv.get_key(".env", "ARDUINO_PORT"), 115200)

def ResetArmMotorPosition():
    arduino_serial.write(bytes([0x10]))

def SetArmMotorPositionValue(pos):

    high = (pos>> 8) & 0xFF;
    low = pos & 0xFF;

    arduino_serial.write(bytes([0x30, high, low]))
    
def OpenClaw():
    arduino_serial.write(bytes([0x21]))

def CloseClaw():
    arduino_serial.write(bytes([0x22]))