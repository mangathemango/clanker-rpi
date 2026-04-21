import serial
import dotenv

arduino_serial = serial.Serial(dotenv.get_key(".env", "ARDUINO_PORT"), 115200)


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