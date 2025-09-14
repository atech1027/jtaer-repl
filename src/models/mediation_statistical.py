
import argparse
import pandas as pd

def fe_ols(y_col, X_cols, df):
    import statsmodels.api as sm
    entities = pd.get_dummies(df['firm_id'], drop_first=True, prefix='f')
    times = pd.get_dummies(df['quarter'], drop_first=True, prefix='t')
    X = pd.concat([pd.Series(1.0, index=df.index, name='const'), df[X_cols], entities, times], axis=1)
    y = df[y_col]
    res = sm.OLS(y, X).fit(cov_type='HC1')
    return res

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--mediator", default="DIO")
    args = ap.parse_args()

    df = pd.read_csv(args.data).dropna(subset=["CCC","IT_lag1", args.mediator]).copy()

    # Try linearmodels; else fallback to OLS+dummies
    try:
        from linearmodels.panel import PanelOLS
        import statsmodels.api as sm
        def run_fe(y, X, d):
            d2 = d.set_index(["firm_id","quarter"]).sort_index()
            mod = PanelOLS(d2[y], sm.add_constant(d2[X]), entity_effects=True, time_effects=True)
            return mod.fit(cov_type="clustered", cluster_entity=True)
        res_M = run_fe(args.mediator, ["IT_lag1"], df)
        res_Y = run_fe("CCC", ["IT_lag1", args.mediator], df)
        a = res_M.params.get("IT_lag1", float('nan'))
        b = res_Y.params.get(args.mediator, float('nan'))
        cprime = res_Y.params.get("IT_lag1", float('nan'))
    except Exception:
        res_M = fe_ols(args.mediator, ["IT_lag1"], df)
        res_Y = fe_ols("CCC", ["IT_lag1", args.mediator], df)
        a = res_M.params.get("IT_lag1", float('nan'))
        b = res_Y.params.get(args.mediator, float('nan'))
        cprime = res_Y.params.get("IT_lag1", float('nan'))

    ab = a*b if (a==a and b==b) else float('nan')
    out = pd.DataFrame({
        "metric": ["a (IT→M)", "b (M→Y|IT)", "c' (IT→Y|M)", "a*b (statistical)"],
        "value": [a, b, cprime, ab]
    })
    out.to_csv(args.out, index=False)
    print(f"Saved mediation -> {args.out}")

if __name__ == "__main__":
    main()
