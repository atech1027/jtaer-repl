
from pathlib import Path
import pandas as pd

def read_csv(path: str) -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return pd.read_csv(p)

def ensure_dir(path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
