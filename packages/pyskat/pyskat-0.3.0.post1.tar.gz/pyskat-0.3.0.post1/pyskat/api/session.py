# pyright: reportInvalidTypeForm=false

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from pyskat.database import DbSessionDep
from pyskat.data_model import (
    Session,
    SessionPublic,
    SessionCreate,
    SessionUpdate,
    SessionPublicDeep,
)


router = APIRouter(
    prefix="/session",
    tags=["session"],
)


@router.get("/", response_model=list[SessionPublic])
async def api_session_get_all(db: DbSessionDep):
    return db.exec(select(Session)).all()


@router.get("/{session_id}", response_model=SessionPublicDeep)
async def api_session_get_single(session_id: int, db: DbSessionDep):
    return db.get(Session, session_id) or raise_not_found(session_id)


@router.post("/", response_model=SessionPublic)
async def api_session_create(session: SessionCreate, db: DbSessionDep):
    db_session = Session.model_validate(session)
    db.add(db_session)
    db.commit()
    return db_session


@router.patch("/{session_id}", response_model=SessionPublic)
async def api_session_update(session_id: int, session: SessionUpdate, db: DbSessionDep):
    db_session = db.get(Session, session_id) or raise_not_found(session_id)
    session_data = session.model_dump(exclude_unset=True)
    db_session.sqlmodel_update(session_data)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


@router.delete("/{session_id}", status_code=204)
async def api_session_delete(session_id: int, db: DbSessionDep):
    db_session = db.get(Session, session_id) or raise_not_found(session_id)
    db.delete(db_session)
    db.commit()


def raise_not_found(session_id: int):
    raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
