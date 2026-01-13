# pyright: reportInvalidTypeForm=false

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from pyskat.database import DbSessionDep
from pyskat.data_model import (
    Result,
    ResultPublic,
    ResultCreate,
    ResultUpdate,
    ResultPublicDeep,
    Match,
    Player,
)
from pyskat.api import match as api_match
from pyskat.api import player as api_player

router = APIRouter(
    prefix="/result",
    tags=["result"],
)


@router.get("/", response_model=list[ResultPublic])
async def api_result_get_all(db: DbSessionDep):
    return db.exec(select(Result)).all()


@router.get("/{match_id}/{player_id}", response_model=ResultPublicDeep)
async def api_result_get_single(player_id: int, match_id: int, db: DbSessionDep):
    return db.get(
        Result, dict(match_id=match_id, player_id=player_id)
    ) or raise_not_found(match_id, player_id)


@router.post("/{match_id}/{player_id}", response_model=ResultPublic)
async def api_result_create(
    match_id: int,
    player_id: int,
    result: ResultCreate,
    db: DbSessionDep,
):
    match = db.get(Match, match_id) or api_match.raise_not_found(match_id)
    _ = db.get(Player, player_id) or api_player.raise_not_found(player_id)
    if player_id not in match.player_ids:
        raise HTTPException(
            status_code=404,
            detail=f"Player {player_id} was not found in match {match_id}.",
        )

    db_result = Result.model_validate(
        result.model_dump() | dict(match_id=match_id, player_id=player_id)
    )
    db.add(db_result)
    db.commit()
    return db_result


@router.patch("/{match_id}/{player_id}", response_model=ResultPublic)
async def api_result_update(
    player_id: int,
    match_id: int,
    result: ResultUpdate,
    db: DbSessionDep,
):
    db_result = db.get(
        Result, dict(match_id=match_id, player_id=player_id)
    ) or raise_not_found(match_id, player_id)
    result_data = result.model_dump(exclude_unset=True)
    db_result.sqlmodel_update(result_data)
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result


@router.delete("/{match_id}/{player_id}", status_code=204)
async def api_result_delete(player_id: int, match_id: int, db: DbSessionDep):
    db_result = db.get(
        Result, dict(match_id=match_id, player_id=player_id)
    ) or raise_not_found(match_id, player_id)
    db.delete(db_result)
    db.commit()


def raise_not_found(match_id: int, player_id: int):
    raise HTTPException(
        status_code=404,
        detail=f"Result for player {player_id} on match {match_id} not found",
    )
