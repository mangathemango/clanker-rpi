import time
from server import config
from server.config import global_config
import robot

while True:
    global_config = config.get_config()
    
    if len(global_config["actionQueue"]) != 0:
        action = global_config["actionQueue"].pop(0)
        config.save_config()
        print(global_config["actionQueue"])
        print("Processing", action["name"])
        robot.process_actions(action["actions"])
    else:
        print("No update :(")
    time.sleep(3)


