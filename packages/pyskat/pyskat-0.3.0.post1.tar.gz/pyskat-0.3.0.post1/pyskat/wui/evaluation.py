from typing import Annotated, Literal
from fastapi import Query, Request
from fastapi.routing import APIRouter
from pyskat.wui.jinja import RenderTemplateDep
from pyskat.settings import SettingsDep
from pyskat.database import DbSessionDep
from pyskat.data_model import Session, Match, Player, to_pandas
from pyskat.api.evaluation import evaluate_matches
from pyskat.wui.sessions import CurrentSessionDep
from pyskat.wui.messages import FlashErrorDep
from sqlmodel import select
import plotly.io as pio
import plotly.express as px
from plotly_bootstrap_templates import load_figure_template

load_figure_template("all")

router = APIRouter(prefix="/evaluation", tags=["evaluation"])


@router.get("/")
def wui_evaluation(
    render_template: RenderTemplateDep,
    db: DbSessionDep,
    settings: SettingsDep,
    request: Request,
    current_session: CurrentSessionDep,
    flash_error: FlashErrorDep,
    sort: Annotated[str, Query()] = "total_score",
    ascending: Annotated[bool, Query()] = False,
    session: int | Literal["current"] | None = None,
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

    matches = db.exec(match_selection).all()
    sessions = db.exec(select(Session)).all()
    players = db.exec(select(Player)).all()

    if matches:
        try:
            evaluation = evaluate_matches(settings.evaluation, matches)
        except ValueError as e:
            evaluation = None
            flash_error(f"Error during evaluation occurred: {e}")
        else:
            evaluation = evaluation.join(
                to_pandas(
                    players,
                    index_col="id",
                    rename_index="player_id",
                    rename_columns={"name": "player_name"},
                    drop_columns=["active", "remarks"],
                )
            )
            evaluation.reset_index(inplace=True)
            evaluation["player_label"] = (
                evaluation["player_name"]
                + " ("
                + evaluation["player_id"].astype("string")
                + ")"
            )
            evaluation.sort_values(by=sort, inplace=True, ascending=ascending)
            evaluation.reset_index(inplace=True, drop=True)
    else:
        evaluation = None

    pio.templates.default = settings.wui.plotly_template
    return render_template(
        "evaluation.html",
        sessions=sessions,
        evaluation_data=evaluation,
        session=session,
        displays=settings.wui.evaluation_displays,
        px=px,
        session_filter=session,
        sort=sort,
        ascending=ascending,
    )
