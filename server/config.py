import json
import os 



def get_config():
    with open("config.json", "r") as conf_json:
        return json.loads(conf_json.read())


config = get_config()

def save_config():
    global config
    with open("config.json", "w") as conf_json:
        conf_json.write(json.dumps(config))

def update_config():
    global config
    config = get_config()
