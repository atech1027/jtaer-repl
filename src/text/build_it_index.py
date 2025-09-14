
import argparse, re, os
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import f1_score, confusion_matrix, classification_report
from sklearn.pipeline import make_pipeline

def load_corpus(input_dir: Path):
    rows = []
    for p in sorted(input_dir.glob("*.txt")):
        text = p.read_text(encoding="utf-8", errors="ignore")
        stem = p.stem  # firm_year
        m = re.match(r"(.+)_([0-9]{4})$", stem)
        if m:
            firm_id, year = m.group(1), m.group(2)
        else:
            firm_id, year = stem, "0000"
        rows.append({"firm_id": firm_id, "year": year, "text": text})
    return pd.DataFrame(rows)

def main():
    ap = argparse.ArgumentParser(description="Build supervised IT index from 10-K text with evaluation")
    ap.add_argument("--input", required=True, help="directory of 10-K .txt files")
    ap.add_argument("--output", required=True, help="output CSV with firm_id,quarter,IT_index")
    ap.add_argument("--labels_csv", help="CSV with columns: firm_id,year,label[,text] for supervised training")
    ap.add_argument("--eval_dir", help="directory to save evaluation tables (csv/txt)")
    args = ap.parse_args()

    input_dir = Path(args.input)
    df_corpus = load_corpus(input_dir)
    if df_corpus.empty:
        raise SystemExit("No .txt files found in input directory.")

    # If labels provided, train supervised classifier
    if args.labels_csv:
        df_lbl = pd.read_csv(args.labels_csv)
        need_cols = {"firm_id","year","label"}
        if not need_cols.issubset(df_lbl.columns):
            raise SystemExit(f"labels_csv must contain columns: {need_cols}")
        # Merge labels onto corpus; prefer labels' text if present
        df = df_corpus.merge(df_lbl, on=["firm_id","year"], how="left", suffixes=("","_lbl"))
        if "text_lbl" in df.columns and df["text_lbl"].notna().any():
            df["text"] = df["text_lbl"].fillna(df["text"])
        # Supervised subset
        train = df.dropna(subset=["label"]).copy()
        train["label"] = train["label"].astype(int)
        # Build pipeline
        pipe = make_pipeline(
            TfidfVectorizer(ngram_range=(1,2), max_features=40000, stop_words="english", min_df=2),
            LogisticRegression(max_iter=200, n_jobs=None)
        )
        # CV predictions for evaluation
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        y_pred = cross_val_predict(pipe, train["text"], train["label"], cv=skf, method="predict")
        y_prob = cross_val_predict(pipe, train["text"], train["label"], cv=skf, method="predict_proba")[:,1]

        f1 = f1_score(train["label"], y_pred)
        cm = confusion_matrix(train["label"], y_pred)
        report = classification_report(train["label"], y_pred, digits=3)

        # Fit on full labeled data for deployment
        pipe.fit(train["text"], train["label"])

        # Predict IT probability for all documents
        it_prob = pipe.predict_proba(df_corpus["text"])[:,1]
        df_corpus["IT_index_raw"] = it_prob

        # Save eval files
        if args.eval_dir:
            Path(args.eval_dir).mkdir(parents=True, exist_ok=True)
            pd.DataFrame({"metric":["F1"], "value":[f1]}).to_csv(Path(args.eval_dir)/"it_eval.csv", index=False)
            pd.DataFrame(cm, columns=["pred_0","pred_1"], index=["true_0","true_1"]).to_csv(Path(args.eval_dir)/"it_confusion_matrix.csv")
            with open(Path(args.eval_dir)/"it_classification_report.txt","w",encoding="utf-8") as f:
                f.write(report)
    else:
        # Fallback: keyword heuristic => proxy score (still numeric)
        KEYWORDS = [
            r"e[-\s]?commerce", r"electronic\s+catalog", r"\bEDI\b", r"platform",
            r"digital\s+marketplace", r"online\s+order", r"B2B\s+portal",
            r"supply\s+chain\s+integration", r"\bAPI\b", r"ERP\s+integration"
        ]
        def kw_score(s:str) -> float:
            sc=0.0
            for kw in KEYWORDS:
                if re.search(kw, s, flags=re.I):
                    sc+=1.0
            return sc
        df_corpus["IT_index_raw"] = df_corpus["text"].apply(kw_score)

    # Z-score standardization across firms/years
    x = df_corpus["IT_index_raw"]
    df_corpus["IT_index"] = (x - x.mean()) / (x.std(ddof=0) if x.std(ddof=0)>0 else 1.0)

    # Expand to quarters
    out_rows = []
    for _, r in df_corpus.iterrows():
        for q in ["Q1","Q2","Q3","Q4"]:
            out_rows.append({
                "firm_id": r["firm_id"],
                "quarter": f"{r['year']}{q}",
                "IT_index": r["IT_index"]
            })
    out = pd.DataFrame(out_rows)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.output, index=False)
    print(f"Wrote {len(out)} rows -> {args.output}")

if __name__ == "__main__":
    main()
