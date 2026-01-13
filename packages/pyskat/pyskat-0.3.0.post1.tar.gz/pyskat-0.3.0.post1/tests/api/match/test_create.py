import pytest
from rich.pretty import pprint


def test_3player(client, faker, add_players):
    res = client.post(
        "/match",
        json={
            "player_ids": [1, 2, 3],
        },
    )
    pprint(res.json())
    assert res.status_code == 200
    assert res.json() == {
        "id": 1,
        "size": 3,
        "player_ids": [1, 2, 3],
        "session_id": None,
        "remarks": "",
    }


def test_4player(client, faker, add_players):
    res = client.post(
        "/match",
        json={
            "player_ids": [1, 2, 3, 4],
        },
    )
    pprint(res.json())
    assert res.status_code == 200
    assert res.json() == {
        "id": 1,
        "size": 4,
        "player_ids": [1, 2, 3, 4],
        "session_id": None,
        "remarks": "",
    }


@pytest.mark.parametrize("place", range(4))
def test_player_non_existent(client, faker, add_players, place: int):
    create_data = {
        "player_ids": [1, 2, 3, 4],
    }
    create_data["player_ids"][place] = 9834795834
    res = client.post("/match", json=create_data)
    pprint(res.json())
    assert res.status_code == 404


def test_remarks(client, faker, add_players):
    remarks = faker.word()

    res = client.post(
        "/match",
        json={"player_ids": [1, 2, 3, 4], "remarks": remarks},
    )
    pprint(res.json())
    assert res.status_code == 200
    assert res.json() == {
        "id": 1,
        "size": 4,
        "player_ids": [1, 2, 3, 4],
        "session_id": None,
        "remarks": remarks,
    }


def test_session_existing(client, faker, add_players):
    client.post("/session", json={"date": faker.date_time().isoformat()})
    res = client.post(
        "/match",
        json={"player_ids": [1, 2, 3, 4], "session_id": 1},
    )
    pprint(res.json())
    assert res.status_code == 200
    assert res.json() == {
        "id": 1,
        "size": 4,
        "player_ids": [1, 2, 3, 4],
        "session_id": 1,
        "remarks": "",
    }


def test_session_non_existing(client, faker, add_players):
    res = client.post(
        "/match",
        json={"player_ids": [1, 2, 3, 4], "session_id": 7846284},
    )
    pprint(res.json())
    assert res.status_code == 404


def test_multiple(client, faker, add_players):
    for i in range(1, 5):
        remarks = faker.word()

        res = client.post(
            "/match",
            json={"player_ids": [1, 2, 3, 4], "remarks": remarks},
        )
        pprint(res.json())
        assert res.status_code == 200
        assert res.json() == {
            "id": i,
            "size": 4,
            "player_ids": [1, 2, 3, 4],
            "session_id": None,
            "remarks": remarks,
        }
