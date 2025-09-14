
import argparse, re
from pathlib import Path

def guess_firm_year(name: str):
    # Accept patterns like firm123_2020.* or 2020_firm123.*
    m = re.search(r'(\d{4})', name)
    year = m.group(1) if m else "0000"
    # firm id = prefix before first '_' or the part without the year
    base = Path(name).stem
    parts = base.split('_')
    if len(parts) >= 2 and re.fullmatch(r'\d{4}', parts[1]):
        firm = parts[0]
    else:
        firm = re.sub(r'\d{4}', '', base).strip('_-') or base
    return firm, year

def clean_text(s: str) -> str:
    # very light cleaner: remove HTML tags
    s = re.sub(r'<[^>]+>', ' ', s, flags=re.S)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def main():
    ap = argparse.ArgumentParser(description="Convert local 10-K files to plain text for IT index")
    ap.add_argument("--input_dir", required=True, help="folder with raw 10-K files (.txt/.html/.htm/pdf-text)")
    ap.add_argument("--out_dir", required=True, help="output folder (data/raw/10k)")
    args = ap.parse_args()

    in_dir = Path(args.input_dir)
    out_dir = Path(args.out_dir); out_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for p in in_dir.glob("*.*"):
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            # binary: skip
            continue
        firm, year = guess_firm_year(p.name)
        out_name = f"{firm}_{year}.txt"
        out_path = out_dir / out_name
        out_path.write_text(clean_text(text), encoding="utf-8")
        count += 1
    print(f"Wrote {count} cleaned 10-K text files to {out_dir}")

if __name__ == "__main__":
    main()
