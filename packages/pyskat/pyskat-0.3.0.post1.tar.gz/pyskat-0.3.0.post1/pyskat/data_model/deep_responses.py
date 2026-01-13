from pyskat.data_model.result import ResultPublic
from pyskat.data_model.player import PlayerPublic
from pyskat.data_model.match import MatchPublic
from pyskat.data_model.session import SessionPublic


class PlayerPublicDeep(PlayerPublic):
    matches: list[MatchPublic] = []
    results: list[ResultPublic] = []


class MatchPublicDeep(MatchPublic):
    session: SessionPublic | None = None
    results: list[ResultPublic] = []
    players: list[PlayerPublic] = []


class ResultPublicDeep(ResultPublic):
    match: MatchPublic | None = None
    player: PlayerPublic | None = None


class SessionPublicDeep(SessionPublic):
    matches: list[MatchPublic] = []
    players: list[PlayerPublic] = []
