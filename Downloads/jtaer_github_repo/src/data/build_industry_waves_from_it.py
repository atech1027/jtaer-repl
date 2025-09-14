
import argparse, pandas as pd
from pathlib import Path

def main():
    ap = argparse.ArgumentParser(description="Derive industry adoption waves from IT_index percentiles")
    ap.add_argument("--it_csv", default="data/interim/it_index.csv")
    ap.add_argument("--industry_map_csv", help="optional CSV with firm_id,industry; if it_csv already has 'industry' column, not needed")
    ap.add_argument("--out", default="data/raw/external/industry_waves.csv")
    ap.add_argument("--percentile", type=float, default=0.6, help="threshold on industry-quarter median IT_index to switch wave to 1")
    args = ap.parse_args()

    it = pd.read_csv(args.it_csv)
    if "industry" not in it.columns:
        if not args.industry_map_csv:
            raise SystemExit("Need industry info via --industry_map_csv or include 'industry' column in it_csv")
        ind = pd.read_csv(args.industry_map_csv)
        it = it.merge(ind, on="firm_id", how="left")

    g = it.groupby(["industry","quarter"])["IT_index"].median().reset_index(name="med_it")
    thr = g.groupby("industry")["med_it"].transform(lambda s: s.quantile(args.percentile))
    g["wave"] = (g["med_it"] >= thr).astype(int)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    g[["industry","quarter","wave"]].to_csv(args.out, index=False)
    print(f"[OK] Wrote {len(g)} rows -> {args.out}")

if __name__ == "__main__":
    main()
