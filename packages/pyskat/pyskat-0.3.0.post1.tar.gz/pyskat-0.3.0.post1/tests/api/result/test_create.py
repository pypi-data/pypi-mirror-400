def test_existing(client, faker, add_matches):
    score = faker.random_int(0, 1000)
    won = faker.random_int(0, 10)
    lost = faker.random_int(0, 10)

    res = client.post(
        "/result/1/2",
        json={
            "score": score,
            "won": won,
            "lost": lost,
        },
    )
    assert res.status_code == 200
    assert res.json() == {
        "match_id": 1,
        "player_id": 2,
        "score": score,
        "won": won,
        "lost": lost,
        "remarks": "",
    }


def test_non_existing(client, faker, add_matches):
    score = faker.random_int(0, 1000)
    won = faker.random_int(0, 10)
    lost = faker.random_int(0, 10)

    res = client.post(
        "/result/8757982/92384982342",
        json={
            "score": score,
            "won": won,
            "lost": lost,
        },
    )
    assert res.status_code == 404
