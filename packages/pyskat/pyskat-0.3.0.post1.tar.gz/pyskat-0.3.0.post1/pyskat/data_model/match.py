# pyright: reportIncompatibleVariableOverride=false

from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from pyskat.data_model.player import Player
    from pyskat.data_model.session import Session
    from pyskat.data_model.result import Result
from pyskat.data_model.player_match_link import PlayerMatchLink

__all__ = ["Match", "MatchPublic", "MatchCreate", "MatchUpdate"]


class MatchBase(SQLModel):
    session_id: int | None = Field(gt=0, default=None, foreign_key="session.id")
    remarks: str = Field(default="")


class Match(MatchBase, table=True):
    id: int | None = Field(gt=0, default=None, primary_key=True)

    results: list["Result"] = Relationship(back_populates="match")
    session: Optional["Session"] = Relationship(back_populates="matches")

    players: list["Player"] = Relationship(
        back_populates="matches", link_model=PlayerMatchLink
    )

    @property
    def player_ids(self) -> list[int]:
        return [p.id or 0 for p in self.players]

    @property
    def size(self) -> int:
        return len(self.players)


class MatchPublic(MatchBase):
    id: int = Field(gt=0, primary_key=True)
    size: int
    player_ids: list[int]


class MatchCreate(MatchBase):
    player_ids: list[int] = []


class MatchUpdate(SQLModel):
    session_id: int | None = Field(gt=0, default=None)
    remarks: str | None = None
    player_ids: list[int] | None = None
    add_player_ids: list[int] | None = None
    del_player_ids: list[int] | None = None


class MatchShuffleSpec(BaseModel):
    session_id: int | None = Field(gt=0, default=None)
    active_only: bool = True
    include: list[int] | None = None
    exclude: list[int] | None = None
    include_only: list[int] | None = None
    prefer_match_size: int = 4
