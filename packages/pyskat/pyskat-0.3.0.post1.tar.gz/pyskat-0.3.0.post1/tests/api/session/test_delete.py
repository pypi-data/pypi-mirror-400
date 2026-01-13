from faker import Faker
from fastapi.testclient import TestClient


def add_session(client: TestClient, faker: Faker):
    name = faker.name()
    date = faker.date_time().isoformat()
    remarks = faker.word()

    res = client.post(
        "/session",
        json={
            "name": name,
            "date": date,
            "remarks": remarks,
        },
    )
    assert res.status_code == 200
    return res.json()


def test_delete(client, faker):
    created_session = add_session(client, faker)

    res = client.delete(f"/session/{created_session['id']}")
    assert res.status_code == 204
    assert client.get(f"/session/{created_session['id']}").status_code == 404


def test_delete_non_existent(client, faker):
    res = client.delete(f"/session/{87537345873}")
    assert res.status_code == 404
