from faker import Faker
from fastapi.testclient import TestClient


def add_session(client: TestClient, faker: Faker):
    for i in range(1, 5):
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
        yield {
            "id": i,
            "name": name,
            "date": date,
            "remarks": remarks,
        }


def test_all(client, faker):
    created_session = list(add_session(client, faker))

    res = client.get("/session")
    assert res.status_code == 200
    assert res.json() == created_session


def test_single(client, faker):
    created_session = list(add_session(client, faker))

    for p in created_session:
        res = client.get(f"/session/{p['id']}")
        assert res.status_code == 200
        res_json = res.json()
        del res_json["players"]
        del res_json["matches"]
        assert res_json == p


def test_single_non_existent(client, faker):
    res = client.get(f"/session/{87537345873}")
    assert res.status_code == 404
