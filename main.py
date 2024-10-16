import asyncio
import logging
import importlib
from contextlib import asynccontextmanager

import socketio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.services.database import DatabaseService
from app.services.meta import MetaDataService

# This is Mint version! Don't change this!
__mintName__ = "Mint"
__mintFrontName__ = "MintBBS"
__mintVersion__ = "0.1.0"
__mintCodeName__ = "Pierrot"


@asynccontextmanager
async def lifespan(app: FastAPI):
    await DatabaseService.connect()
    await MetaDataService.load(name=__mintFrontName__)
    logging.getLogger("uvicorn").info(
        f"Metadata {MetaDataService.metadata.name} (ID: {MetaDataService.metadata.id}) was loaded!"
    )
    yield
    async with asyncio.timeout(60):
        await DatabaseService.pool.close()


fastapi = FastAPI(
    title=__mintName__,
    version=__mintVersion__,
    summary=f"{__mintName__} v{__mintVersion__} Codename: {__mintCodeName__}",
    lifespan=lifespan,
)
sio = socketio.AsyncServer()
app = socketio.ASGIApp(sio, fastapi)

fastapi.mount("/static", StaticFiles(directory="static"), name="static")

fastapi.include_router(importlib.import_module("app.routes.index").router)
fastapi.include_router(importlib.import_module("app.routes.api.boards.show").router)
fastapi.include_router(
    importlib.import_module("app.routes.api.admin.request_admin").router
)
fastapi.include_router(importlib.import_module("app.routes.api.admin.login").router)
