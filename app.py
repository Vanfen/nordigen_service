from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from router import app_router
from starlette.middleware.sessions import SessionMiddleware

def include_routers(app):
    app.include_router(app_router)

def start_application():
    app = FastAPI(title="Nordigen app", version="1.0.0")
    app.mount("/package", StaticFiles(directory="package"), name="package")
    app.add_middleware(SessionMiddleware, secret_key="random-string-that-will-be-the-key")
    include_routers(app)
    return app

app = start_application()
