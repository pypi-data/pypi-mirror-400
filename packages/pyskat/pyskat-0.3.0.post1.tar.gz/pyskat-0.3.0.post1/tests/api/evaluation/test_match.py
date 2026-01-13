from fastapi.testclient import TestClient
import pandas as pd
from io import StringIO


def test_match(client: TestClient, faker, add_results, add_matches):
    res = client.get(
        "/evaluation/match/1",
    )

    assert res.status_code == 200
    df = pd.read_csv(StringIO(res.text))

    assert not df.won_score.isna().all()
    assert not df.lost_score.isna().all()
    assert not df.opponents_lost_score.isna().all()
    assert not df.total_score.isna().all()


def test_match_missing_results(client, faker, add_matches):
    res = client.get(
        "/evaluation/match/1",
    )

    assert res.status_code == 500
