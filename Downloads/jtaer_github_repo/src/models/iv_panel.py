
import argparse, pandas as pd, numpy as np

def two_stage_ols(df, y_col, endog_cols, exog_df, instr_df):
    import statsmodels.api as sm
    # Align and drop NaNs across all needed columns
    full = pd.concat([df[[y_col] + endog_cols], exog_df, instr_df], axis=1).dropna()
    y = full[y_col]
    endog = full[endog_cols]
    exog = full[exog_df.columns]
    instr = full[instr_df.columns]
    # First stage
    Z = pd.concat([pd.Series(1.0, index=full.index, name='const'), exog, instr], axis=1)
    Xhat = {}
    for c in endog.columns:
        res1 = sm.OLS(endog[c], Z).fit()
        Xhat[c] = res1.fittedvalues
    Xhat_df = pd.DataFrame(Xhat, index=full.index)
    # Second stage
    X2 = pd.concat([pd.Series(1.0, index=full.index, name='const'), exog, Xhat_df], axis=1)
    res2 = sm.OLS(y, X2).fit(cov_type="HC1")
    return res2

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--endog", default="IT_lag1")
    ap.add_argument("--instr", default="IV_peer_IT")
    args = ap.parse_args()

    df = pd.read_csv(args.data).dropna(subset=["CCC", args.endog, "gscpi"]).copy()

    entities = pd.get_dummies(df['firm_id'], drop_first=True, prefix='f')
    times = pd.get_dummies(df['quarter'], drop_first=True, prefix='t')
    exog_df = pd.concat([df[["gscpi"]], entities, times], axis=1)

    endog_cols = [args.endog, f"{args.endog}xGSCPI"]
    df[f"{args.endog}xGSCPI"] = df[args.endog] * df["gscpi"]

    if args.instr not in df.columns:
        raise SystemExit(f"Missing instrument column: {args.instr}")
    instr_df = pd.concat([df[[args.instr]], df[[args.instr]].mul(df['gscpi'], axis=0).rename(columns={args.instr:f'{args.instr}xGSCPI'})], axis=1)

    try:
        from linearmodels.iv import IV2SLS
        import statsmodels.api as sm
        full = pd.concat([df[["CCC"] + endog_cols], exog_df, instr_df], axis=1).dropna()
        X = pd.concat([pd.Series(1.0, index=full.index, name="const"), full[exog_df.columns]], axis=1)
        endog = full[endog_cols]
        instr = full[instr_df.columns]
        mod = IV2SLS(full["CCC"], X, endog, instr)
        res = mod.fit(cov_type="robust")
        out = res.summary.as_text()
    except Exception as e:
        res = two_stage_ols(df, "CCC", endog_cols, exog_df, instr_df)
        out = str(res.summary()) + "\n\n[Note] Fallback 2SLS via two-stage OLS (HC1). Dropped rows with NaNs."

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"Saved IV results -> {args.out}")

if __name__ == "__main__":
    main()
