def test_all(client, faker, add_results):
    res = client.get("/result")
    assert res.status_code == 200
    assert res.json() == add_results


def test_single(client, faker, add_results):
    for r in add_results:
        res = client.get(f"/result/{r['match_id']}/{r['player_id']}")
        assert res.status_code == 200
        res_json = res.json()
        del res_json["player"]
        del res_json["match"]
        assert res_json == r


def test_single_non_existent(client, faker, add_results):
    res = client.get("/result/6545/537345873")
    assert res.status_code == 404
