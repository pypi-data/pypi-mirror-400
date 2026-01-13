from datetime import datetime
from typing import Annotated
from fastapi import Request, Depends
from fastapi.routing import APIRouter
from sqlmodel import select

from pyskat.wui.jinja import RenderTemplateDep
from pyskat.database import DbSessionDep
from pyskat.data_model import Session, SessionPublic
from pyskat.api.session import raise_not_found
from pyskat.wui.messages import FlashWarningDep


router = APIRouter(prefix="/sessions", tags=["session"])


def get_current_session(db: DbSessionDep, request: Request) -> Session | None:
    current_id = request.session.get("current_session_id", None)
    if current_id:
        current = db.get(Session, int(current_id)) or raise_not_found(current_id)
        return current


def set_current_session(
    db: DbSessionDep, request: Request, session_id: int | None
) -> Session | None:
    session = (
        db.get(Session, session_id) or raise_not_found(session_id)
        if session_id is not None
        else None
    )
    request.session["current_session_id"] = session_id
    return session


def current_session_dep(db: DbSessionDep, request: Request) -> Session | None:
    try:
        return get_current_session(db, request)
    except:  # noqa: E722
        return None


CurrentSessionDep = Annotated[Session | None, Depends(current_session_dep)]


@router.get("/")
def wui_sessions(
    render_template: RenderTemplateDep,
    db: DbSessionDep,
    request: Request,
    flash_warning: FlashWarningDep,
    current_session: CurrentSessionDep,
):
    sessions = db.exec(select(Session)).all()

    if not current_session:
        flash_warning("No current session set.")

    return render_template(
        "sessions.html",
        sessions=sessions,
        current_session=current_session,
        now=datetime.today().isoformat(sep=" ", timespec="minutes"),
    )


@router.get("/current", response_model=SessionPublic | None)
def wui_sessions_get_current(db: DbSessionDep, request: Request):
    return get_current_session(db, request)


@router.patch("/current/{session_id}", response_model=SessionPublic)
def wui_sessions_set_current(session_id: int, db: DbSessionDep, request: Request):
    return set_current_session(db, request, session_id)


@router.delete("/current", response_model=SessionPublic | None)
def wui_sessions_delete_current(db: DbSessionDep, request: Request):
    return set_current_session(db, request, None)
