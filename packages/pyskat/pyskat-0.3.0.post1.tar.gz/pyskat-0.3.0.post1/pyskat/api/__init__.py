from fastapi import FastAPI

from pyskat.api import player
from pyskat.api import match
from pyskat.api import session
from pyskat.api import result
from pyskat.api import evaluation

__all__ = ["create_app"]


def create_app() -> FastAPI:
    app = FastAPI()

    app.include_router(player.router)
    app.include_router(match.router)
    app.include_router(session.router)
    app.include_router(result.router)
    app.include_router(evaluation.router)

    return app
