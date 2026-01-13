# pyright: reportIncompatibleVariableOverride=false

from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyskat.data_model.match import Match
    from pyskat.data_model.player import Player


class ResultBase(SQLModel):
    score: int
    won: int = Field(ge=0)
    lost: int = Field(ge=0)
    remarks: str = ""


class Result(ResultBase, table=True):
    player_id: int = Field(default=0, gt=0, foreign_key="player.id", primary_key=True)
    match_id: int = Field(default=0, gt=0, foreign_key="match.id", primary_key=True)

    match: "Match" = Relationship(back_populates="results")
    player: "Player" = Relationship(back_populates="results")


class ResultPublic(ResultBase):
    player_id: int = Field(gt=0)
    match_id: int = Field(gt=0)


class ResultCreate(ResultBase):
    pass


class ResultUpdate(SQLModel):
    score: int | None = None
    won: int | None = Field(ge=0, default=None)
    lost: int | None = Field(ge=0, default=None)
    remarks: str | None = None
