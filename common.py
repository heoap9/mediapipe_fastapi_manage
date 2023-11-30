from fastapi import FastAPI
from starlette.templating import Jinja2Templates

def create_app():
    app = FastAPI()
    templates = Jinja2Templates(directory="templates")
    return app, templates