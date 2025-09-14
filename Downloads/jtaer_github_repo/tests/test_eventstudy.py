
import pandas as pd
from src.models.did_eventstudy import run_eventstudy

def test_eventstudy_runs(tmp_path):
    df = pd.DataFrame({
        'firm_id': ['a','a','b','b'],
        'quarter': ['2019Q1','2019Q2','2019Q1','2019Q2'],
        'CCC': [10, 12, 9, 11],
        'event_time': [-2, 0, -1, 1]
    })
    out = run_eventstudy(df, out_csv=None, fig_path=None, window=1)
    assert not out.empty
