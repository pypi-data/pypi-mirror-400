def test_delete(client, faker, add_match):
    res = client.delete(f"/match/{add_match['id']}")
    assert res.status_code == 204
    assert client.get(f"/match/{add_match['id']}").status_code == 404


def test_delete_non_existent(client, faker):
    res = client.delete(f"/match/{87537345873}")
    assert res.status_code == 404
