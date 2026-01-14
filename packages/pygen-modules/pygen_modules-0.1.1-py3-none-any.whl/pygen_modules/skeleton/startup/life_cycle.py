from typing import Awaitable, Callable
from fastapi import FastAPI
from dbconfig.database import Database


def register_startup_event(app: FastAPI) -> Callable[[], Awaitable[None]]:
    @app.on_event("startup")
    async def _startup() -> None:
        Database.createDBTables()

    return _startup


def register_shutdown_event(app: FastAPI) -> Callable[[], Awaitable[None]]:
    @app.on_event("shutdown")
    async def _shutdown() -> None:
        print("[SHUTDOWN] Application shutting down cleanly.")

    return _shutdown
