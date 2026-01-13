# pyright: reportIncompatibleVariableOverride=false

from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyskat.data_model.player import Player
    from pyskat.data_model.match import Match

__all__ = ["Session", "SessionPublic", "SessionCreate", "SessionUpdate"]


class SessionBase(SQLModel):
    name: str = ""
    date: datetime
    remarks: str = ""


class Session(SessionBase, table=True):
    id: int | None = Field(ge=0, default=None, primary_key=True)

    matches: list["Match"] = Relationship(back_populates="session")

    @property
    def players(self) -> list["Player"]:
        return [p for t in self.matches for p in t.players]


class SessionPublic(SessionBase):
    id: int = Field(ge=0, primary_key=True)


class SessionCreate(SessionBase):
    pass


class SessionUpdate(SQLModel):
    name: str | None = None
    date: datetime | None = None
    remarks: str | None = None
