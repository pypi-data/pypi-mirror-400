from faker import Faker
from fastapi.testclient import TestClient


def add_player(client: TestClient, faker: Faker):
    name = faker.name()
    active = faker.boolean()
    remarks = faker.word()

    res = client.post(
        "/player", json={"name": name, "active": active, "remarks": remarks}
    )
    assert res.status_code == 200
    return res.json()


def test_name(client, faker):
    created_player = add_player(client, faker)
    new_name = faker.name()

    res = client.patch(f"/player/{created_player['id']}", json={"name": new_name})
    assert res.status_code == 200
    assert res.json() == created_player | {"name": new_name}


def test_active(client, faker):
    created_player = add_player(client, faker)
    new_active = not created_player["active"]

    res = client.patch(f"/player/{created_player['id']}", json={"active": new_active})
    assert res.status_code == 200
    assert res.json() == created_player | {"active": new_active}


def test_remarks(client, faker):
    created_player = add_player(client, faker)
    new_remarks = faker.word()

    res = client.patch(f"/player/{created_player['id']}", json={"remarks": new_remarks})
    assert res.status_code == 200
    assert res.json() == created_player | {"remarks": new_remarks}


def test_name_active_remarks(client, faker):
    created_player = add_player(client, faker)
    new_name = faker.name()
    new_active = not created_player["active"]
    new_remarks = faker.word()

    res = client.patch(
        f"/player/{created_player['id']}",
        json={
            "name": new_name,
            "active": new_active,
            "remarks": new_remarks,
        },
    )
    assert res.status_code == 200
    assert res.json() == created_player | {
        "name": new_name,
        "active": new_active,
        "remarks": new_remarks,
    }


def test_non_existent(client, faker):
    res = client.patch(f"/player/{984379843}", json={})
    assert res.status_code == 404
