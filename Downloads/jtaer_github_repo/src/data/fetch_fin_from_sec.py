
import argparse, sys, time, json, re, math
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd
import requests
from datetime import datetime

UA = "YourName-YourOrg-Contact@example.com"  # replace with your email per SEC API guidance

FACT_TAGS = {
    "sales": ["SalesRevenueNet", "Revenues"],
    "cogs": ["CostOfGoodsSold"],
    "inventory": ["InventoryNet", "Inventory"],
    "receivables": ["AccountsReceivableNetCurrent"],
    "payables": ["AccountsPayableCurrent"],
}

def to_quarter(dt: str) -> str:
    d = pd.to_datetime(dt)
    return f"{d.year}Q{((d.month-1)//3)+1}"

def get_cik_for_ticker(ticker: str) -> Optional[str]:
    # Use SEC submissions endpoint (no key) to resolve ticker to CIK
    url = f"https://data.sec.gov/submissions/CIK0000000000.json"  # placeholder to check format
    # We will instead use the "tickers" list JSON
    resp = requests.get("https://www.sec.gov/files/company_tickers.json", headers={"User-Agent": UA}, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    for _, row in data.items():
        if row.get("ticker","").upper() == ticker.upper():
            cik = str(row["cik_str"]).zfill(10)
            return cik
    return None

def pick_facts(cfacts: dict, tags: List[str]) -> List[dict]:
    # Return all fact entries across provided tags
    out = []
    facts = cfacts.get("facts", {}).get("us-gaap", {})
    for tag in tags:
        if tag in facts:
            for uom, arr in facts[tag].get("units", {}).items():
                for item in arr:
                    # item has "start", "end" (for duration), or only "end" (for instant), and "val"
                    out.append({"tag": tag, "uom": uom, **item})
    return out

def best_unit(rows: List[dict]) -> str:
    # prefer USD
    uoms = [r["uom"] for r in rows]
    if "USD" in uoms: return "USD"
    return uoms[0] if uoms else "USD"

def build_fin_for_cik(cik: str) -> pd.DataFrame:
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    cf = requests.get(url, headers={"User-Agent": UA}, timeout=60).json()
    series = {}
    for k, tags in FACT_TAGS.items():
        rows = pick_facts(cf, tags)
        if not rows:
            continue
        u = best_unit(rows)
        rows = [r for r in rows if r["uom"] == u]
        # Build quarter series
        recs = []
        for r in rows:
            end = r.get("end")
            if not end:  # skip if no end
                continue
            q = to_quarter(end)
            val = r.get("val")
            # Keep last filed per quarter
            recs.append({"quarter": q, "val": val, "filed": r.get("filed","") , "accn": r.get("accn","")})
        s = pd.DataFrame(recs).sort_values(["quarter","filed"]).groupby("quarter", as_index=False).last()
        series[k] = s[["quarter","val"]].rename(columns={"val": k})

    # Merge series on quarter
    fin = None
    for k, s in series.items():
        fin = s if fin is None else fin.merge(s, on="quarter", how="outer")
    if fin is None:
        return pd.DataFrame()
    fin["cik"] = cik
    return fin

def main():
    ap = argparse.ArgumentParser(description="Fetch quarterly fin.csv from SEC companyfacts API")
    ap.add_argument("--tickers_csv", help="CSV with column 'ticker' (alternatively use --ciks_csv)")
    ap.add_argument("--ciks_csv", help="CSV with column 'cik' (10-digit, leading zeros allowed)")
    ap.add_argument("--out", required=True, help="output CSV path, e.g., data/raw/fin.csv")
    ap.add_argument("--industry_map_csv", help="optional CSV with columns cik,industry")
    args = ap.parse_args()

    if not args.tickers_csv and not args.ciks_csv:
        sys.exit("Provide --tickers_csv or --ciks_csv")

    tickers = []
    ciks = []

    if args.tickers_csv:
        tdf = pd.read_csv(args.tickers_csv)
        tickers = [t for t in tdf["ticker"].dropna().astype(str).tolist() if t.strip()]

    if args.ciks_csv:
        cdf = pd.read_csv(args.ciks_csv)
        ciks = [str(c).zfill(10) for c in cdf["cik"].dropna().astype(int).tolist()]

    # Resolve tickers to CIKs
    for t in tickers:
        cik = get_cik_for_ticker(t)
        if cik:
            ciks.append(cik)
        else:
            print(f"[WARN] Ticker {t} not found in SEC tickers list.")

    rows = []
    for cik in sorted(set(ciks)):
        print(f"[INFO] Fetching companyfacts for CIK {cik}")
        df = build_fin_for_cik(cik)
        if df.empty:
            print(f"[WARN] No facts for {cik}")
            continue
        df["firm_id"] = cik  # use CIK as firm_id
        rows.append(df)

        time.sleep(0.2)  # be gentle

    if not rows:
        sys.exit("No data fetched.")

    fin = pd.concat(rows, ignore_index=True)
    # Reorder and add industry if provided
    cols = ["firm_id","quarter","sales","cogs","inventory","receivables","payables"]
    for c in cols:
        if c not in fin.columns: fin[c] = None
    fin = fin[cols]

    if args.industry_map_csv:
        im = pd.read_csv(args.industry_map_csv)
        fin = fin.merge(im[["cik","industry"]].rename(columns={"cik":"firm_id"}), on="firm_id", how="left")
    else:
        fin["industry"] = None

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    fin.to_csv(args.out, index=False)
    print(f"[OK] Wrote {len(fin)} rows -> {args.out}")

if __name__ == "__main__":
    main()
