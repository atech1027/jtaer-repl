
import argparse
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt

def design_matrices(df, window=6):
    # Build leads/lags dummies for event_time in [-window, +window], omit -1 as baseline
    for k in range(-window, window+1):
        df[f"E{k}"] = (df["event_time"] == k).astype(int)
    baseline = -1
    cols = [f"E{k}" for k in range(-window, window+1) if k != baseline]
    # FE via dummies
    entities = pd.get_dummies(df['firm_id'], drop_first=True, prefix='f')
    times = pd.get_dummies(df['quarter'], drop_first=True, prefix='t')
    X = pd.concat([pd.Series(1.0, index=df.index, name='const'), df[cols], entities, times], axis=1)
    return X, cols

def run_eventstudy(df, out_csv=None, fig_path=None, window=6):
    dfx = df.dropna(subset=["CCC","event_time"]).copy()
    X, cols = design_matrices(dfx, window=window)
    y = dfx["CCC"]
    model = sm.OLS(y, X)
    res = model.fit(cov_type="HC1")

    table = pd.DataFrame({
        "term": cols,
        "coef": res.params[cols].values,
        "std_err": res.bse[cols].values,
        "p_value": res.pvalues[cols].values,
    })
    # term -> k
    table["k"] = table["term"].str.replace("E", "").astype(int)
    table = table.sort_values("k")

    if out_csv:
        table.to_csv(out_csv, index=False)

    if fig_path:
        plt.figure()
        k = table["k"]; b = table["coef"]; se = table["std_err"]
        ci_lo = b - 1.96*se
        ci_hi = b + 1.96*se
        plt.plot(k, b, marker='o', label='β_k')
        plt.fill_between(k, ci_lo, ci_hi, alpha=0.2, label='95% CI')
        plt.axhline(0, linestyle='--')
        plt.axvline(-1, linestyle=':')  # baseline
        plt.title('Event Study (baseline = -1)')
        plt.xlabel('Event time k')
        plt.ylabel('Effect on CCC')
        plt.legend()
        plt.tight_layout()
        plt.savefig(fig_path, dpi=180)

    return table

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="processed CSV with event_time")
    ap.add_argument("--out", help="output CSV for event-study terms" )
    ap.add_argument("--fig", help="output figure path (png)" )
    ap.add_argument("--window", type=int, default=6, help="lead/lag window" )
    args = ap.parse_args()

    df = pd.read_csv(args.data)
    run_eventstudy(df, out_csv=args.out, fig_path=args.fig, window=args.window)

if __name__ == '__main__':
    main()
