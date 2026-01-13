import pandas as pd
from io import StringIO


def test_session(client, faker, add_results, add_session, add_players):
    res = client.get(
        "/evaluation/session/1",
    )

    assert res.status_code == 200
    df = pd.read_csv(StringIO(res.text))

    assert not df.won_score.isna().all()
    assert not df.lost_score.isna().all()
    assert not df.opponents_lost_score.isna().all()
    assert not df.total_score.isna().all()
