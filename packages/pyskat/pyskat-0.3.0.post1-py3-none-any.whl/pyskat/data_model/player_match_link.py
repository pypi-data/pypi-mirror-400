# pyright: reportIncompatibleVariableOverride=false

from sqlmodel import SQLModel, Field

__all__ = [
    "PlayerMatchLink",
    "PlayerMatchLinkPublic",
    "PlayerMatchLinkCreate",
]


class PlayerMatchLinkBase(SQLModel):
    player_id: int = Field(default=None, foreign_key="player.id", primary_key=True)
    match_id: int = Field(default=None, foreign_key="match.id", primary_key=True)


class PlayerMatchLink(PlayerMatchLinkBase, table=True):
    pass


class PlayerMatchLinkPublic(PlayerMatchLinkBase):
    pass


class PlayerMatchLinkCreate(PlayerMatchLinkBase):
    pass
