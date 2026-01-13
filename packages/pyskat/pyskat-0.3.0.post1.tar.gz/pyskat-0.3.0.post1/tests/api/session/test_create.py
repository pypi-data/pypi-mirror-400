def test_date(client, faker):
    date = faker.date_time().isoformat()

    res = client.post("/session", json={"date": date})
    assert res.status_code == 200
    assert res.json() == {
        "id": 1,
        "name": "",
        "date": date,
        "remarks": "",
    }


def test_date_name(client, faker):
    date = faker.date_time().isoformat()
    name = faker.name()

    res = client.post("/session", json={"date": date, "name": name})
    assert res.status_code == 200
    assert res.json() == {
        "id": 1,
        "name": name,
        "date": date,
        "remarks": "",
    }


def test_date_remarks(client, faker):
    date = faker.date_time().isoformat()
    remarks = faker.word()

    res = client.post(
        "/session",
        json={"date": date, "remarks": remarks},
    )
    assert res.status_code == 200
    assert res.json() == {
        "id": 1,
        "name": "",
        "date": date,
        "remarks": remarks,
    }


def test_date_name_remarks(client, faker):
    date = faker.date_time().isoformat()
    name = faker.name()
    remarks = faker.word()

    res = client.post(
        "/session",
        json={
            "date": date,
            "name": name,
            "remarks": remarks,
        },
    )
    assert res.status_code == 200
    assert res.json() == {
        "id": 1,
        "name": name,
        "date": date,
        "remarks": remarks,
    }


def test_multiple(client, faker):
    for i in range(1, 5):
        date = faker.date_time().isoformat()
        name = faker.name()
        remarks = faker.word()

        res = client.post(
            "/session",
            json={
                "date": date,
                "name": name,
                "remarks": remarks,
            },
        )
        assert res.status_code == 200
        assert res.json() == {
            "id": i,
            "name": name,
            "date": date,
            "remarks": remarks,
        }
