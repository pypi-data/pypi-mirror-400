# pyright: reportIncompatibleVariableOverride=false

from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyskat.data_model.result import Result
    from pyskat.data_model.match import Match

from pyskat.data_model.player_match_link import PlayerMatchLink

__all__ = ["Player", "PlayerPublic", "PlayerCreate", "PlayerUpdate"]


class PlayerBase(SQLModel):
    name: str
    active: bool = True
    remarks: str = ""


class Player(PlayerBase, table=True):
    id: int | None = Field(gt=0, default=None, primary_key=True)

    matches: list["Match"] = Relationship(
        back_populates="players", link_model=PlayerMatchLink
    )
    results: list["Result"] = Relationship(back_populates="player")


class PlayerPublic(PlayerBase):
    id: int = Field(gt=0)


class PlayerCreate(PlayerBase):
    pass


class PlayerUpdate(SQLModel):
    name: str | None = None
    active: bool | None = None
    remarks: str | None = None
