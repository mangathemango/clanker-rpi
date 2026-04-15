from server import app
import uvicorn

uvicorn.run(app=app, port=8000)


