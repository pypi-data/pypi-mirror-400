def test_score(client, faker, add_result):
    new_score = faker.random_int(0, 1000)

    res = client.patch("/result/1/2", json={"score": new_score})
    assert res.status_code == 200
    assert res.json() == add_result | {"score": new_score}


def test_won(client, faker, add_result):
    new_won = faker.random_int(0, 10)

    res = client.patch("/result/1/2", json={"won": new_won})
    assert res.status_code == 200
    assert res.json() == add_result | {"won": new_won}


def test_lost(client, faker, add_result):
    new_lost = faker.random_int(0, 10)

    res = client.patch("/result/1/2", json={"lost": new_lost})
    assert res.status_code == 200
    assert res.json() == add_result | {"lost": new_lost}


def test_remarks(client, faker, add_result):
    new_remarks = faker.word()

    res = client.patch("/result/1/2", json={"remarks": new_remarks})
    assert res.status_code == 200
    assert res.json() == add_result | {"remarks": new_remarks}


def test_non_existent(client, faker, add_results):
    res = client.patch("/result/984379843/4242", json={})
    assert res.status_code == 404
