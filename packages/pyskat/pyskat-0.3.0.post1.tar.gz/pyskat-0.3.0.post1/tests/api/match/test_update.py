import pytest
from faker import Faker
from fastapi.testclient import TestClient


def add_match(client: TestClient, faker: Faker):
    for i in range(1, 9):
        name = faker.name()
        client.post("/player", json={"name": name})

    remarks = faker.word()
    res = client.post(
        "/match",
        json={
            "player_ids": [1, 2, 3, 4],
            "remarks": remarks,
        },
    )
    assert res.status_code == 200
    return res.json()


def test_remarks(client, faker):
    created_table = add_match(client, faker)
    new_remarks = faker.word()

    res = client.patch(f"/match/{created_table['id']}", json={"remarks": new_remarks})
    assert res.status_code == 200
    assert res.json() == created_table | {"remarks": new_remarks}


def test_non_existent(client, faker):
    res = client.patch(f"/match/{984379843}", json={})
    assert res.status_code == 404


def test_player_ids(client, faker):
    created_table = add_match(client, faker)
    res = client.patch(
        f"/match/{created_table['id']}", json={"player_ids": [5, 6, 7, 8]}
    )
    assert res.status_code == 200
    assert res.json() == created_table | {"player_ids": [5, 6, 7, 8]}


@pytest.mark.parametrize("place", range(4))
def test_player_ids_non_existent(client, faker, place: int):
    created_table = add_match(client, faker)
    player_ids = [5, 6, 7, 8]
    player_ids[place] = 897933985
    res = client.patch(f"/match/{created_table['id']}", json={"player_ids": player_ids})
    assert res.status_code == 404


def test_session_existing(client, faker):
    created_table = add_match(client, faker)
    client.post("/session", json={"date": faker.date_time().isoformat()})
    res = client.patch(f"/match/{created_table['id']}", json={"session_id": 1})
    assert res.status_code == 200
    assert res.json() == created_table | {"session_id": 1}


def test_session_non_existing(client, faker):
    created_table = add_match(client, faker)
    res = client.patch(f"/match/{created_table['id']}", json={"session_id": 8798324})
    assert res.status_code == 404
