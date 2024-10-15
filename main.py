import importlib
from contextlib import asynccontextmanager

import socketio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# This is Mint version! Don't change this!
__mintName__ = "Mint"
__mintVersion__ = "0.1.0"
__mintCodeName__ = "Pierrot"

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

fastapi = FastAPI(title=__mintName__, version=__mintVersion__, summary=f"{__mintName__} v{__mintVersion__} Codename: {__mintCodeName__}", lifespan=lifespan)
sio = socketio.AsyncServer()
app = socketio.ASGIApp(sio, fastapi)

fastapi.mount("/static", StaticFiles(directory="static"), name="static")

fastapi.include_router(importlib.import_module("app.routes.index").router)
