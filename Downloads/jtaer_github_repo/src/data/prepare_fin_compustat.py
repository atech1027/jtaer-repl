
import argparse
import pandas as pd

def to_quarter_str(dt):
    if not isinstance(dt, pd.Timestamp):
        dt = pd.to_datetime(dt)
    q = ((dt.month-1)//3)+1
    return f"{dt.year}Q{q}"

def main():
    ap = argparse.ArgumentParser(description="Convert Compustat FUNDQ export -> data/raw/fin.csv schema")
    ap.add_argument("--input", required=True, help="Compustat FUNDQ CSV")
    ap.add_argument("--out", required=True, help="output CSV path (data/raw/fin.csv)")
    # column names (override if your export uses different headers)
    ap.add_argument("--firm_id_col", default="gvkey")
    ap.add_argument("--date_col", default="datadate")
    ap.add_argument("--sales_col", default="saleq")
    ap.add_argument("--cogs_col", default="cogsq")
    ap.add_argument("--inventory_col", default="invtq")
    ap.add_argument("--receivables_col", default="rectq")
    ap.add_argument("--payables_col", default="apq")
    ap.add_argument("--industry_col", default="naics", help="optional; will be included if present")
    args = ap.parse_args()

    df = pd.read_csv(args.input, low_memory=False)
    cols = [args.firm_id_col, args.date_col, args.sales_col, args.cogs_col,
            args.inventory_col, args.receivables_col, args.payables_col]
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise SystemExit(f"Missing columns in input: {missing}")

    out_cols = {
        "firm_id": args.firm_id_col,
        "quarter": args.date_col,
        "sales": args.sales_col,
        "cogs": args.cogs_col,
        "inventory": args.inventory_col,
        "receivables": args.receivables_col,
        "payables": args.payables_col,
    }
    out = df.rename(columns=out_cols)[list(out_cols.keys())].copy()
    # Quarter string
    out["quarter"] = pd.to_datetime(out["quarter"]).apply(to_quarter_str)

    # Optional industry
    if args.industry_col in df.columns:
        out["industry"] = df[args.industry_col].astype(str)
    else:
        out["industry"] = None

    # Drop rows with any essential NaNs (you may relax this)
    out = out.dropna(subset=["sales","cogs","inventory","receivables","payables"])

    # Aggregate duplicates within firm_id-quarter by summing flows and taking last stocks
    flows = out.groupby(["firm_id","quarter"], as_index=False).agg({
        "sales":"sum", "cogs":"sum",
        "inventory":"last", "receivables":"last", "payables":"last",
        "industry":"last"
    })

    flows.to_csv(args.out, index=False)
    print(f"Wrote standardized fin.csv -> {args.out} (rows={len(flows)})")

if __name__ == "__main__":
    main()
