from rich.pretty import pprint


def test_shuffle_prefer(client, faker, add_players, player_count=11):
    res = client.post(
        "/match/create_shuffled",
        json={
            "prefer_match_size": 3,
        },
    )
    pprint(res.json())
    assert res.status_code == 200
    assert len(res.json()) == 4


def test_shuffle_active_only(client, faker, add_players, player_count=11):
    client.patch("/player/12", json={"active": False})

    res = client.post(
        "/match/create_shuffled",
        json={
            "prefer_match_size": 3,
        },
    )
    pprint(res.json())
    assert res.status_code == 200
    assert len(res.json()) == 3


def test_shuffle_include(client, faker, add_players, player_count=11):
    client.patch("/player/12", json={"active": False})

    res = client.post(
        "/match/create_shuffled",
        json={"prefer_match_size": 3, "include": [12]},
    )
    pprint(res.json())
    assert res.status_code == 200
    assert len(res.json()) == 4


def test_shuffle_exclude(client, faker, add_players, player_count=11):
    res = client.post(
        "/match/create_shuffled",
        json={"prefer_match_size": 3, "exclude": [12]},
    )
    pprint(res.json())
    assert res.status_code == 200
    assert len(res.json()) == 3


def test_shuffle_include_only(client, faker, add_players, player_count=11):
    res = client.post(
        "/match/create_shuffled",
        json={"prefer_match_size": 3, "include_only": [1, 2, 3, 4]},
    )
    pprint(res.json())
    assert res.status_code == 200
    assert len(res.json()) == 1
