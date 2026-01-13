def test_delete(client, add_result):
    res = client.delete("/result/1/2")
    assert res.status_code == 204
    assert client.get("/result/1/2").status_code == 404


def test_delete_non_existent(client, faker, add_results):
    res = client.delete("/result/87537/345873")
    assert res.status_code == 404
