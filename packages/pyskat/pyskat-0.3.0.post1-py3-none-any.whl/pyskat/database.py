from typing import Annotated, Generator
from fastapi import Depends
from functools import lru_cache
from pyskat.settings import SettingsDep

import sqlalchemy
import sqlmodel


@lru_cache
def get_db_engine(url: str):
    engine = sqlalchemy.create_engine(url, connect_args=dict(check_same_thread=False))
    sqlmodel.SQLModel.metadata.create_all(engine)
    return engine


def db_engine_dep(settings: SettingsDep) -> sqlalchemy.Engine:
    return get_db_engine(str(settings.database_url))


DbEngineDep = Annotated[sqlalchemy.Engine, Depends(db_engine_dep)]


def db_session_dep(engine: DbEngineDep) -> Generator[sqlmodel.Session, None, None]:
    with sqlmodel.Session(engine) as session:
        yield session


DbSessionDep = Annotated[sqlmodel.Session, Depends(db_session_dep)]
