import asyncio
import importlib
import logging
import os
from contextlib import asynccontextmanager

import socketio
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
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
    default_response_class=ORJSONResponse,
)
sio = socketio.AsyncServer()
app = socketio.ASGIApp(sio, fastapi)

fastapi.mount("/static", StaticFiles(directory="static"), name="static")

routes_dir = "app/routes"


def autoIncludeRouters(app: FastAPI, base_dir: str):
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                module_path = (
                    os.path.join(root, file).replace("/", ".").replace("\\", ".")[:-3]
                )

                module = importlib.import_module(module_path)

                if hasattr(module, "router"):
                    app.include_router(getattr(module, "router"))


autoIncludeRouters(fastapi, routes_dir)
