
import argparse
from pathlib import Path
import pandas as pd

# Downloads NY Fed GSCPI (xlsx) and saves to CSV with columns quarter,gscpi
URL = "https://www.newyorkfed.org/medialibrary/research/interactives/gscpi/downloads/gscpi_data.xlsx"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/raw/external/gscpi.csv")
    args = ap.parse_args()

    df = pd.read_excel(URL, sheet_name=0)
    # Attempt to sanitize to quarter,gscpi
    # The xlsx usually contains a column named "Date" monthly; we convert to YYYYQ and take mean per quarter
    date_col = None
    for cand in ["Date","DATE","date"]:
        if cand in df.columns:
            date_col = cand; break
    if date_col is None:
        raise SystemExit("Unexpected GSCPI sheet format; please open the xlsx and save as CSV manually.")
    df["quarter"] = pd.to_datetime(df[date_col]).dt.to_period("Q").astype(str).str.replace("Q","Q")
    value_col = [c for c in df.columns if c.lower() not in [date_col.lower(),"quarter"]][0]
    out = df.groupby("quarter", as_index=False)[value_col].mean().rename(columns={value_col:"gscpi"})
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.out, index=False)
    print(f"[OK] Saved {len(out)} quarterly rows -> {args.out}")

if __name__ == "__main__":
    main()
