
import argparse
import pandas as pd
import numpy as np

def fe_via_statsmodels(df: pd.DataFrame):
    import statsmodels.api as sm
    # Build dummies for firm and quarter FE
    entities = pd.get_dummies(df['firm_id'], drop_first=True, prefix='f')
    times = pd.get_dummies(df['quarter'], drop_first=True, prefix='t')
    X = pd.concat([pd.Series(1.0, index=df.index, name='const'),
                   df[['IT_lag1','gscpi']],
                   df[['IT_lag1']].mul(df['gscpi'], axis=0).rename(columns={'IT_lag1':'ITxGSCPI'}),
                   entities, times], axis=1)
    y = df['CCC']
    res = sm.OLS(y, X).fit(cov_type='HC1')
    out_df = pd.DataFrame({
        "term": res.params.index,
        "coef": res.params.values,
        "std_err": res.bse.values,
        "p_value": res.pvalues.values,
    })
    return res, out_df

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    df = pd.read_csv(args.data)
    df = df.dropna(subset=["CCC","IT_lag1","gscpi"]).copy()

    try:
        from linearmodels.panel import PanelOLS
        import statsmodels.api as sm
        df2 = df.copy()
        df2["ITxGSCPI"] = df2["IT_lag1"] * df2["gscpi"]
        df2 = df2.set_index(["firm_id","quarter"]).sort_index()
        y = df2["CCC"]
        X = sm.add_constant(df2[["IT_lag1","gscpi","ITxGSCPI"]])
        mod = PanelOLS(y, X, entity_effects=True, time_effects=True)
        res = mod.fit(cov_type="clustered", cluster_entity=True)
        out_df = pd.DataFrame({
            "term": res.params.index,
            "coef": res.params.values,
            "std_err": res.std_errors.values,
            "p_value": res.pvalues.values,
        })
    except Exception as e:
        # Fallback with statsmodels OLS + dummies
        res, out_df = fe_via_statsmodels(df)

    out_df.to_csv(args.out, index=False)
    print(f"Saved FE table -> {args.out} (rows={len(out_df)})")

if __name__ == "__main__":
    main()
