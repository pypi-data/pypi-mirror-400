# pyright: reportInvalidTypeForm=false

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from fastapi.exceptions import HTTPException
from sqlmodel import select
import pandas as pd
from typing import Any, Sequence

from pyskat.settings import EvaluationSettings, SettingsDep
from pyskat.database import DbSessionDep
from pyskat.data_model import Match, Session, to_pandas
from pyskat.api import match as api_match
from pyskat.api import session as api_session


router = APIRouter(
    prefix="/evaluation",
    tags=["evaluation"],
)


class CSVResponse(PlainTextResponse):
    media_type = "text/csv"

    def render(self, content: Any) -> bytes | memoryview:
        if content is None:
            return b""
        if isinstance(content, (pd.DataFrame, pd.Series)):
            return content.to_csv().encode(self.charset)  # type: ignore
        raise TypeError("Content must be None or a pandas DataFrame/Series")


def evaluate_match(settings: EvaluationSettings, match: Match) -> pd.DataFrame:
    if match.size != len(match.results):
        raise ValueError(f"Results missing for match {match.id}")

    df = to_pandas(match.results, index_col="player_id", drop_columns="remarks")

    df["score"] = df.score * settings.game_score_multiplier
    df["won_score"] = df.won * settings.won_score
    df["lost_score"] = df.lost * settings.lost_score
    df["opponents_lost"] = df.lost.sum() - df.lost
    df["opponents_lost_score"] = df[
        "opponents_lost"
    ] * settings.get_opponent_lost_score(match.size)
    df["total_score"] = (
        df.score + df.won_score + df.lost_score + df.opponents_lost_score
    )

    return df


def evaluate_matches(
    settings: EvaluationSettings, matches: Sequence[Match]
) -> pd.DataFrame:
    df = pd.concat(
        [evaluate_match(settings, m) for m in matches],
    )
    df.reset_index(inplace=True)
    return df.groupby("player_id").sum()  # type:ignore


@router.get("/match/{match_id}", response_class=CSVResponse)
async def api_evaluate_match(db: DbSessionDep, match_id: int, settings: SettingsDep):
    match = db.get(Match, match_id) or api_match.raise_not_found(match_id)
    try:
        evaluation = evaluate_match(settings.evaluation, match)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return CSVResponse(evaluation)


@router.get("/session/{session_id}", response_class=CSVResponse)
async def api_evaluate_session(
    db: DbSessionDep, session_id: int, settings: SettingsDep
):
    session = db.get(Session, session_id) or api_session.raise_not_found(session_id)
    try:
        evaluation = evaluate_matches(settings.evaluation, session.matches)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return CSVResponse(evaluation)


@router.get("/total", response_class=CSVResponse)
async def api_evaluate_total(db: DbSessionDep, settings: SettingsDep):
    matches = db.exec(select(Match)).all()
    try:
        evaluation = evaluate_matches(settings.evaluation, matches)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return CSVResponse(evaluation)
