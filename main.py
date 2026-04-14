import json
import os
from server import config
from server.api import app
import uvicorn

conf = config.get_config()
conf["cv"]["hsv"]["red"]["lower1"] = 0
config.update_config(conf)

uvicorn.run(app=app)

