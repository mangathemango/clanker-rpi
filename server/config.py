import json
import os 

def get_config():
    with open("config.json", "r") as conf_json:
        return json.loads(conf_json.read())


global_config = get_config()

def save_config():
    global global_config
    print("Saving config")
    with open("config.json", "w") as conf_json:
        conf_json.write(json.dumps(global_config))
    

def save_config_str(str):
    global global_config
    global_config = json.loads(str)
    save_config()

def update_config():
    global global_config
    global_config = get_config()
