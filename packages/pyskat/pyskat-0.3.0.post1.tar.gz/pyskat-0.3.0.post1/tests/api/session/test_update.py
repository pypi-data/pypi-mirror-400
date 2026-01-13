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


def test_name(client, faker):
    created_session = add_session(client, faker)
    new_name = faker.name()

    res = client.patch(f"/session/{created_session['id']}", json={"name": new_name})
    assert res.status_code == 200
    assert res.json() == created_session | {"name": new_name}


def test_date(client, faker):
    created_session = add_session(client, faker)
    new_date = faker.date_time().isoformat()

    res = client.patch(f"/session/{created_session['id']}", json={"date": new_date})
    assert res.status_code == 200
    assert res.json() == created_session | {"date": new_date}


def test_remarks(client, faker):
    created_session = add_session(client, faker)
    new_remarks = faker.word()

    res = client.patch(
        f"/session/{created_session['id']}", json={"remarks": new_remarks}
    )
    assert res.status_code == 200
    assert res.json() == created_session | {"remarks": new_remarks}


def test_name_date_remarks(client, faker):
    created_session = add_session(client, faker)
    new_name = faker.name()
    new_date = faker.date_time().isoformat()
    new_remarks = faker.word()

    res = client.patch(
        f"/session/{created_session['id']}",
        json={
            "name": new_name,
            "date": new_date,
            "remarks": new_remarks,
        },
    )
    assert res.status_code == 200
    assert res.json() == created_session | {
        "name": new_name,
        "date": new_date,
        "remarks": new_remarks,
    }


def test_non_existent(client, faker):
    res = client.patch(f"/session/{984379843}", json={})
    assert res.status_code == 404
