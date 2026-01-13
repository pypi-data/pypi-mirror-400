# pyright: reportInvalidTypeForm=false

from fastapi import APIRouter, HTTPException
from sqlmodel import col, select, or_

from pyskat.data_model.match import MatchShuffleSpec
from pyskat.data_model.shuffle_matches import shuffle_players_to_matches
from pyskat.database import DbSessionDep
from pyskat.data_model import (
    Match,
    MatchPublic,
    MatchPublicDeep,
    MatchCreate,
    MatchUpdate,
    Player,
    Session,
)


router = APIRouter(
    prefix="/match",
    tags=["match"],
)


@router.get("/", response_model=list[MatchPublic])
async def api_match_get_all(db: DbSessionDep):
    return db.exec(select(Match)).all()


@router.get("/{match_id}", response_model=MatchPublicDeep)
async def api_match_get_single(match_id: int, db: DbSessionDep):
    return db.get(Match, match_id) or raise_not_found(match_id)


@router.post("/", response_model=MatchPublic)
async def api_match_create(match: MatchCreate, db: DbSessionDep):
    from pyskat.api import player
    from pyskat.api import session

    db_match = Match.model_validate(match)
    db_match.players = [
        db.get(Player, pid) or player.raise_not_found(pid) for pid in match.player_ids
    ]
    if match.session_id is not None:
        db_match.session = db.get(Session, match.session_id) or session.raise_not_found(
            match.session_id
        )
    db.add(db_match)
    db.commit()
    return db_match


@router.patch("/{match_id}", response_model=MatchPublic)
async def api_match_update(match_id: int, match: MatchUpdate, db: DbSessionDep):
    from pyskat.api import player
    from pyskat.api import session

    db_match = db.get(Match, match_id) or raise_not_found(match_id)
    db_match.sqlmodel_update(match.model_dump(exclude_unset=True))
    if match.player_ids is not None:
        db_match.players = [
            db.get(Player, pid) or player.raise_not_found(pid)
            for pid in match.player_ids
        ]
    if match.add_player_ids is not None:
        for pid in match.add_player_ids:
            db_match.players.append(db.get(Player, pid) or player.raise_not_found(pid))
    if match.del_player_ids is not None:
        for pid in match.del_player_ids:
            db_match.players.remove(db.get(Player, pid) or player.raise_not_found(pid))
    if match.session_id is not None:
        db_match.session = db.get(Session, match.session_id) or session.raise_not_found(
            match.session_id
        )
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match


@router.delete("/{match_id}", status_code=204)
async def api_match_delete(match_id: int, db: DbSessionDep):
    db_match = db.get(Match, match_id) or raise_not_found(match_id)
    db.delete(db_match)
    db.commit()


@router.post("/create_shuffled", response_model=list[MatchPublic])
async def api_match_create_shuffled(db: DbSessionDep, spec: MatchShuffleSpec):
    from pyskat.api import session

    if spec.include_only is not None:
        query = select(Player).where(col(Player.id).in_(spec.include_only))
    else:
        query = select(Player)

        if spec.active_only:
            query = query.where(
                or_(col(Player.active), col(Player.id).in_(spec.include or []))
            )

        query = query.where(col(Player.id).not_in(spec.exclude or []))

    players = list(db.exec(query).all())
    try:
        shuffle = shuffle_players_to_matches(players, spec.prefer_match_size)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    def _yield_matches():
        for s in shuffle:
            db_match = Match()
            db_match.players = s
            if spec.session_id is not None:
                db_match.session = db.get(
                    Session, spec.session_id
                ) or session.raise_not_found(spec.session_id)
            db.add(db_match)
            yield db_match

    matches = list(_yield_matches())
    db.commit()
    return matches


def raise_not_found(match_id: int):
    raise HTTPException(status_code=404, detail=f"Match {match_id} not found")
