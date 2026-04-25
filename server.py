from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

import config
import importlib
import actions
import cv2
import io
from cv import line_guard



app = FastAPI()

app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
)

try:
    from hardware import arduino, esp32
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
except Exception as e:
    print(e)

@app.get("/getLineGuardFrame")
def get_line_guard_frame(color: str = "gray", orientation: str = "straight", camera_index: int = 0):
    frame = line_guard.get_line_guard_frame(color, orientation, camera_index)
    if frame is None:
        return JSONResponse({"error": "Could not capture frame"}, status_code=500)
    
    success, encoded_img = cv2.imencode('.png', frame)
    if not success:
        return JSONResponse({"error": "Could not encode image"}, status_code=500)
    
    img_bytes = encoded_img.tobytes()
    return StreamingResponse(io.BytesIO(img_bytes), media_type="image/png")

@app.get("/config")
def get_config():
    return JSONResponse(config.get_config())

@app.post("/updateConfig")
def update_config(data: dict):
    config.save_config_str(data["config"])

@app.post("/executeActions")
def execute_actions():
    try:
        importlib.reload(actions)
        actions.main()
    except Exception as e:
        print(e)


@app.post("/updateActionScript")
def update_action_script(data: dict):
    with open("actions.py", "w") as f:
        bytes = f.write(data["actionScript"])
        print(f"Written {bytes} bytes into action.py")