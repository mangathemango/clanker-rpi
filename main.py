import json
import os
from server import config
from server.api import app
import uvicorn

uvicorn.run(app=app, port=8000)

