from fastapi import Request
from fastapi.routing import APIRouter
from sqlmodel import select
from typing import Literal

from pyskat.wui.jinja import RenderTemplateDep
from pyskat.database import DbSessionDep
from pyskat.data_model import Match, Session, Player, Result
from pyskat.wui.messages import FlashErrorDep
from pyskat.wui.sessions import CurrentSessionDep


router = APIRouter(prefix="/results", tags=["result"])


@router.get("/")
def wui_results(
    render_template: RenderTemplateDep,
    db: DbSessionDep,
    request: Request,
    current_session: CurrentSessionDep,
    flash_error: FlashErrorDep,
    session: int | Literal["current"] | None = None,
    player: int | None = None,
):
    match_selection = select(Match)

    match session:
        case "current":
            if current_session:
                match_selection = match_selection.where(
                    Match.session_id == current_session.id
                )
            else:
                flash_error("No current session set.")
                match_selection = match_selection.where(False)
        case int():
            match_selection = match_selection.where(Match.session_id == session)
        case None:
            pass

    match player:
        case int():
            match_selection = match_selection.where(
                Match.players.any(Player.id == player)
            )
        case None:
            pass

    matches = db.exec(match_selection).all()
    players = db.exec(select(Player)).all()
    sessions = db.exec(select(Session)).all()
    results = {(r.match_id, r.player_id): r for r in db.exec(select(Result)).all()}
    return render_template(
        "results.html",
        matches=matches,
        players=players,
        sessions=sessions,
        results=results,
        request=request,
        player_filter=player,
        session_filter=session,
    )
