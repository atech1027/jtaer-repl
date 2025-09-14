
import argparse, pathlib, numpy as np, pandas as pd, re

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True, help='output raw data dir')
    args = ap.parse_args()

    outdir = pathlib.Path(args.out)
    (outdir / '10k').mkdir(parents=True, exist_ok=True)
    (outdir / 'external').mkdir(parents=True, exist_ok=True)

    np.random.seed(7)
    firms = [f"firm{n:03d}" for n in range(1, 41)]
    industries = ['31', '32', '33', '34']  # NAICS2-like
    quarters = [f"{y}Q{q}" for y in range(2018, 2023) for q in [1,2,3,4]]

    rows = []
    for f in firms:
        base_sales = np.random.uniform(8e7, 2.2e8)
        ind = np.random.choice(industries)
        for q in quarters:
            sales = base_sales * np.random.uniform(0.9, 1.1)
            cogs = sales * np.random.uniform(0.62, 0.82)
            inventory = np.random.uniform(8e6, 3.5e7)
            receivables = sales * np.random.uniform(0.10, 0.20)
            payables = cogs * np.random.uniform(0.07, 0.16)
            rows.append({
                'firm_id': f,
                'quarter': q,
                'industry': ind,
                'sales': round(sales,2),
                'cogs': round(cogs,2),
                'inventory': round(inventory,2),
                'receivables': round(receivables,2),
                'payables': round(payables,2),
            })
    fin = pd.DataFrame(rows).sort_values(['firm_id','quarter'])
    fin.to_csv(outdir / 'fin.csv', index=False)

    # GSCPI toy series + shock threshold defining treatment start
    qtrs = sorted(fin['quarter'].unique())
    g = np.linspace(-0.4, 1.1, num=len(qtrs))
    gscpi = pd.DataFrame({'quarter': qtrs, 'gscpi': g})
    gscpi.to_csv(outdir / 'external' / 'gscpi.csv', index=False)

    # 10-K minimal texts with keyword variety + labels
    labels = []
    for f in firms:
        year = '2020'
        if np.random.rand() > 0.4:
            txt = "We expanded our B2B e-commerce portal and EDI connections. API integrations with ERP. Online order processing."
            label = 1
        else:
            txt = "Traditional channels remained important; limited platform adoption this year without significant EDI expansion."
            label = 0
        (outdir / '10k' / f"{f}_{year}.txt").write_text(txt, encoding='utf-8')
        labels.append({"firm_id": f, "year": year, "label": label})
    pd.DataFrame(labels).to_csv(outdir / "it_labels.csv", index=False)

    # Optional industry adoption waves for IV demo
    waves = []
    for i, ind in enumerate(industries):
        # simple staggered waves: each industry adopts at a different quarter index
        for idx, q in enumerate(qtrs):
            waves.append({"industry": ind, "quarter": q, "wave": 1 if idx >= (i+2)*2 else 0})
    pd.DataFrame(waves).to_csv(outdir / "external/industry_waves.csv", index=False)

    print(f"Wrote synthetic raw data (incl. it_labels.csv & industry_waves.csv) to {outdir}")

if __name__ == '__main__':
    main()
