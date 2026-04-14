import sys

sys.path.append("..")

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from server import config
from hardware import arduino, esp32

app = FastAPI()

app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
)


@app.get("/frame")
def get_frame():
    return FileResponse("../frame.jpg", media_type="image/jpeg")

@app.post("/setArmMotorPositionUp")
def set_arm_motor_position_up():
    arduino.set_arm_motor_position_up()

@app.post("/setArmMotorPositionDown")
def reset_arm_motor_position():
    arduino.set_arm_motor_position_down()

@app.post("/resetArmMotorPosition")
def reset_arm_motor_position():
    arduino.reset_arm_motor_position()

@app.post("/resetArmMotorPosition")
def reset_arm_motor_position():
    arduino.reset_arm_motor_position()

@app.post("/motorSetSpeed")
def motor_set_speed(data):
    motor = data.motor
    speed = data.speed
    esp32.motor_set_speed(motor, speed)

@app.get("/config")
def get_config():
    return JSONResponse(config.get_config())
