
import argparse
from pathlib import Path
import pandas as pd
import numpy as np

def winsorize(s, lower=0.01, upper=0.99):
    lo = s.quantile(lower)
    hi = s.quantile(upper)
    return s.clip(lower=lo, upper=hi)

def add_treat_and_event(df, rule: str, gscpi_thresh: float = 0.5, custom_events_csv: str = None, shock_col: str = "gscpi"):
    df = df.copy()
    if rule == "gscpi_thresh":
        df["treat"] = (df[shock_col] > gscpi_thresh).astype(int)
        # first treat per firm
        df["first_treat"] = df.groupby("firm_id")["treat"].transform(lambda s: s.idxmax() if s.any() else pd.NA)
    elif rule == "industry_topdecile":
        # within each quarter, mark industries in top 10% shock as treated
        if "industry" not in df.columns:
            raise ValueError("industry_topdecile requires 'industry' column.")
        qg = df.groupby("quarter")[shock_col]
        thr = qg.transform(lambda s: s.quantile(0.9))
        df["treat"] = (df[shock_col] >= thr).astype(int)
        df["first_treat"] = df.groupby("firm_id")["treat"].transform(lambda s: s.idxmax() if s.any() else pd.NA)
    elif rule == "custom_dates":
        if not custom_events_csv:
            raise ValueError("custom_dates requires --custom_events CSV with columns firm_id,event_quarter")
        ev = pd.read_csv(custom_events_csv)
        need = {"firm_id","event_quarter"}
        if not need.issubset(ev.columns):
            raise ValueError("custom_events CSV must have firm_id,event_quarter")
        df = df.merge(ev, on="firm_id", how="left")
        df["treat"] = (df["quarter"] >= df["event_quarter"]).astype(int)
        # locate index of first treat
        df["first_treat"] = df.groupby("firm_id")["treat"].transform(lambda s: s.idxmax() if s.any() else pd.NA)
    else:
        raise ValueError("Unknown treat rule")

    # Quarter numeric index
    qnum = df["quarter"].str.extract(r"(\d{4})Q(\d)").astype(int)
    df["q_index"] = (qnum[0] - qnum[0].min())*4 + (qnum[1]-1)

    # First treat index by firm
    first_idx = df.loc[df.groupby("firm_id")["treat"].transform("idxmax")].set_index("firm_id")["q_index"].to_dict()
    df["event_time"] = df.apply(lambda r: r["q_index"] - first_idx.get(r["firm_id"], r["q_index"]), axis=1)

    return df.drop(columns=["first_treat"])

def add_iv(df, spec: str, iv_lag: int = 4, industry_wave_csv: str = None):
    df = df.copy()
    if spec == "peer_it_lagK":
        if "industry" not in df.columns:
            raise ValueError("peer_it_lagK requires 'industry' column.")
        peer = df.groupby(["industry","quarter"])["IT_index"].transform("mean") - df["IT_index"]
        df["IV_peer_IT"] = peer.groupby(df["firm_id"]).shift(iv_lag)
    elif spec == "industry_wave":
        if not industry_wave_csv:
            raise ValueError("industry_wave requires --industry_wave_csv with industry,quarter,wave columns")
        waves = pd.read_csv(industry_wave_csv)
        need = {"industry","quarter","wave"}
        if not need.issubset(waves.columns):
            raise ValueError("industry_wave CSV requires columns industry,quarter,wave")
        df = df.merge(waves, on=["industry","quarter"], how="left")
        df["IV_wave"] = df["wave"]
    else:
        raise ValueError("Unknown IV spec")
    return df

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fin", required=True, help="firm-quarter financials CSV")
    ap.add_argument("--gscpi", required=True, help="GSCPI CSV with columns: quarter,gscpi")
    ap.add_argument("--it", required=True, help="IT index CSV with columns: firm_id,quarter,IT_index")
    ap.add_argument("--out", required=True, help="output CSV path")

    # New options
    ap.add_argument("--treat_rule", default="gscpi_thresh", choices=["gscpi_thresh","industry_topdecile","custom_dates"])
    ap.add_argument("--gscpi_thresh", type=float, default=0.5)
    ap.add_argument("--custom_events", help="CSV with firm_id,event_quarter for custom treatment timing")
    ap.add_argument("--shock_col", default="gscpi")

    ap.add_argument("--iv_spec", default="peer_it_lagK", choices=["peer_it_lagK","industry_wave"])
    ap.add_argument("--iv_lag", type=int, default=4)
    ap.add_argument("--industry_wave_csv", help="CSV with industry,quarter,wave (for industry_wave IV)")

    args = ap.parse_args()

    fin = pd.read_csv(args.fin)
    gscpi = pd.read_csv(args.gscpi)
    it = pd.read_csv(args.it)

    # Core metrics
    fin["DIO"] = 365.0 * fin["inventory"] / fin["cogs"].replace(0, np.nan)
    fin["DSO"] = 365.0 * fin["receivables"] / fin["sales"].replace(0, np.nan)
    fin["DPO"] = 365.0 * fin["payables"] / fin["cogs"].replace(0, np.nan)
    fin["CCC"] = fin[["DIO","DSO","DPO"]].apply(lambda r: r[0]+r[1]-r[2], axis=1)

    # Merge
    df = fin.merge(it, on=["firm_id","quarter"], how="left")
    df = df.merge(gscpi, on="quarter", how="left")

    # Lagged IT
    df = df.sort_values(["firm_id","quarter"])
    df["IT_lag1"] = df.groupby("firm_id")["IT_index"].shift(1)

    # Winsorize
    for col in ["CCC","DIO","DSO","DPO"]:
        df[col] = winsorize(df[col])

    # Treat & event_time
    df = add_treat_and_event(df, rule=args.treat_rule, gscpi_thresh=args.gscpi_thresh, custom_events_csv=args.custom_events, shock_col=args.shock_col)

    # Instruments
    df = add_iv(df, spec=args.iv_spec, iv_lag=args.iv_lag, industry_wave_csv=args.industry_wave_csv)

    # Drop rows with missing essentials
    df = df.dropna(subset=["CCC","IT_lag1","gscpi"]).reset_index(drop=True)

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)
    print(f"Processed rows: {len(df)} -> {args.out}")

if __name__ == "__main__":
    main()
