
import pandas as pd
from src.features.compute_ccc import winsorize

def test_winsorize_basic():
    s = pd.Series([1,2,3,1000])
    w = winsorize(s, 0.25, 0.75)
    assert w.min() >= s.quantile(0.25) - 1e-9
    assert w.max() <= s.quantile(0.75) + 1e-9
