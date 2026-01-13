from faker import Faker
from fastapi.testclient import TestClient


def add_players(client: TestClient, faker: Faker):
    for i in range(1, 5):
        name = faker.name()
        active = faker.boolean()
        remarks = faker.word()

        res = client.post(
            "/player", json={"name": name, "active": active, "remarks": remarks}
        )
        assert res.status_code == 200
        yield {
            "id": i,
            "name": name,
            "active": active,
            "remarks": remarks,
        }


def test_all(client, faker):
    created_players = list(add_players(client, faker))

    res = client.get("/player")
    assert res.status_code == 200
    assert res.json() == created_players


def test_single(client, faker):
    created_players = list(add_players(client, faker))

    for p in created_players:
        res = client.get(f"/player/{p['id']}")
        assert res.status_code == 200
        res_json = res.json()
        del res_json["results"]
        del res_json["matches"]
        assert res_json == p


def test_single_non_existent(client, faker):
    res = client.get(f"/player/{87537345873}")
    assert res.status_code == 404
