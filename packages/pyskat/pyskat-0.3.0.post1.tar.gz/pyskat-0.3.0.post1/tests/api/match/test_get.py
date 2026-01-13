def test_all(client, faker, add_matches):
    res = client.get("/match")
    assert res.status_code == 200
    assert res.json() == add_matches


def test_single(client, faker, add_matches):
    for p in add_matches:
        res = client.get(f"/match/{p['id']}")
        assert res.status_code == 200
        res_json = res.json()
        del res_json["players"]
        del res_json["session"]
        del res_json["results"]
        assert res_json == p


def test_single_non_existent(client, faker, add_matches):
    res = client.get(f"/match/{87537345873}")
    assert res.status_code == 404
