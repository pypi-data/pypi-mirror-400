def test_name(client, faker):
    name = faker.name()

    res = client.post("/player", json={"name": name})
    assert res.status_code == 200
    assert res.json() == {
        "id": 1,
        "name": name,
        "active": True,
        "remarks": "",
    }


def test_name_remarks(client, faker):
    name = faker.name()
    remarks = faker.word()

    res = client.post("/player", json={"name": name, "remarks": remarks})
    assert res.status_code == 200
    assert res.json() == {
        "id": 1,
        "name": name,
        "active": True,
        "remarks": remarks,
    }


def test_name_active(client, faker):
    name = faker.name()
    active = faker.boolean()

    res = client.post("/player", json={"name": name, "active": active})
    assert res.status_code == 200
    assert res.json() == {
        "id": 1,
        "name": name,
        "active": active,
        "remarks": "",
    }


def test_name_active_remarks(client, faker):
    name = faker.name()
    active = faker.boolean()
    remarks = faker.word()

    res = client.post(
        "/player", json={"name": name, "active": active, "remarks": remarks}
    )
    assert res.status_code == 200
    assert res.json() == {
        "id": 1,
        "name": name,
        "active": active,
        "remarks": remarks,
    }


def test_multiple(client, faker):
    for i in range(1, 5):
        name = faker.name()
        active = faker.boolean()
        remarks = faker.word()

        res = client.post(
            "/player", json={"name": name, "active": active, "remarks": remarks}
        )
        assert res.status_code == 200
        assert res.json() == {
            "id": i,
            "name": name,
            "active": active,
            "remarks": remarks,
        }
