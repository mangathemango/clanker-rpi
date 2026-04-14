import json
import os 

def get_config():
    with open("config.json", "r") as conf_json:
        return json.loads(conf_json.read())
    
def update_config(conf):
    with open("config.json", "w") as conf_json:
        conf_json.write(json.dumps(conf))