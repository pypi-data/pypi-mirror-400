from datetime import datetime
from fastapi import FastAPI
import pytest
from faker import Faker
from fastapi.testclient import TestClient
import sqlmodel
from pyskat.data_model import Player, Session, Result, Match
from pyskat.settings import Settings, settings_dep
from pyskat.database import get_db_engine
import pyskat.api
import pyskat.wui


@pytest.fixture
def settings(tmp_path, monkeypatch):
    settings = Settings(
        database_url=f"sqlite:///{tmp_path}/test.db",
    )
    return settings


@pytest.fixture
def db_session(settings: Settings):
    engine = get_db_engine(settings.database_url)
    with sqlmodel.Session(engine) as session:
        yield session


@pytest.fixture
def api_app(settings, monkeypatch) -> FastAPI:
    app = pyskat.api.create_app()
    app.debug = True
    app.dependency_overrides = {settings_dep: lambda: settings}
    return app


@pytest.fixture
def wui_app(settings, monkeypatch, api_app) -> FastAPI:
    app = pyskat.wui.create_app(api_app)
    app.debug = True
    app.dependency_overrides = {settings_dep: lambda: settings}
    return app


@pytest.fixture
def client(api_app) -> TestClient:
    client = TestClient(api_app)
    return client


@pytest.fixture
def faker():
    return Faker()


@pytest.fixture
def add_players(db_session, faker, request):
    def yield_players():
        for i in range(1, 12 + 1):
            name = faker.name()
            db_session.add(Player(name=name))
            yield dict(id=i, name=name, remarks="")
        db_session.commit()

    return list(yield_players())


@pytest.fixture
def add_match(db_session, add_players, faker):
    remarks = faker.word()
    db_session.add(
        Match(players=[db_session.get(Player, i) for i in range(1, 5)], remarks=remarks)
    )
    db_session.commit()
    return dict(id=1, player_ids=list(range(1, 5)), remarks=remarks)


@pytest.fixture
def add_matches(db_session, faker, add_players):
    def yield_matches():
        for i in range(1, 3 + 1):
            i0 = 4 * (i - 1)
            pids = [1 + i0, 2 + i0, 3 + i0, 4 + i0]
            remarks = faker.word()
            db_session.add(
                Match(
                    players=[db_session.get(Player, i) for i in pids],
                    remarks=remarks,
                )
            )
            db_session.commit()
            yield dict(id=i, player_ids=pids, remarks=remarks, size=4, session_id=None)

    return list(yield_matches())


@pytest.fixture
def add_result(db_session, faker: Faker, add_match):
    score = faker.random_int(0, 1000)
    won = faker.random_int(0, 10)
    lost = faker.random_int(0, 10)

    db_session.add(Result(match_id=1, player_id=2, score=score, won=won, lost=lost))
    db_session.commit()
    return dict(match_id=1, player_id=2, score=score, won=won, lost=lost, remarks="")


@pytest.fixture
def add_results(db_session, faker: Faker, add_matches):
    def yield_results():
        for m in add_matches:
            for p in m["player_ids"]:
                score = faker.random_int(0, 1000)
                won = faker.random_int(0, 10)
                lost = faker.random_int(0, 10)

                db_session.add(
                    Result(
                        match_id=m["id"], player_id=p, score=score, won=won, lost=lost
                    )
                )
                db_session.commit()
                yield dict(
                    match_id=m["id"],
                    player_id=p,
                    score=score,
                    won=won,
                    lost=lost,
                    remarks="",
                )

    return list(yield_results())


@pytest.fixture
def add_session(db_session, faker: Faker, add_matches):
    name = faker.country()
    date = datetime.fromisoformat(faker.date())
    remarks = faker.word()

    db_session.add(
        Session(
            name=name,
            date=date,
            remarks=remarks,
            matches=[db_session.get(Match, m["id"]) for m in add_matches],
        )
    )
    db_session.commit()
    return dict(id=1, name=name, date=date, remarks=remarks)
