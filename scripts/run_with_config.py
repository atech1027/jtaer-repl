
import argparse, subprocess, sys, yaml, pathlib, shutil

def run(cmd: str):
    print(f"[RUN] {cmd}")
    res = subprocess.run(cmd, shell=True)
    if res.returncode != 0:
        sys.exit(res.returncode)

def main():
    ap = argparse.ArgumentParser(description="Run the full pipeline using config/config.yaml")
    ap.add_argument("--config", default="config/config.yaml")
    args = ap.parse_args()

    cfg = yaml.safe_load(pathlib.Path(args.config).read_text(encoding="utf-8"))

    # 1) Prepare private data -> public schema
    compustat = cfg["paths"]["compustat_csv"]
    tenk_dir  = cfg["paths"]["tenk_raw_dir"]
    run(f"python -m src.data.prepare_fin_compustat --input {compustat} --out data/raw/fin.csv")
    run(f"python -m src.data.prepare_10k_sec --input_dir {tenk_dir} --out_dir data/raw/10k")

    # 2) Train IT index if requested
    if cfg.get("run", {}).get("train_it", False):
        labels_csv = cfg["paths"].get("it_labels_csv", "")
        eval_dir = "reports/tables"
        run(f"python -m src.text.build_it_index --input data/raw/10k --labels_csv {labels_csv} --output data/interim/it_index.csv --eval_dir {eval_dir}")
    else:
        run("python -m src.text.build_it_index --input data/raw/10k --output data/interim/it_index.csv")

    # 3) Validate
    gscpi_csv = cfg["paths"]["gscpi_csv"]
    run(f"python -m src.features.validate --fin data/raw/fin.csv --gscpi {gscpi_csv}")

    # 4) Build processed panel with treat/IV
    treat = cfg["treat"]
    iv    = cfg["iv"]

    treat_args = f"--treat_rule {treat['rule']} --gscpi_thresh {treat.get('gscpi_thresh',0.5)} --shock_col {treat.get('shock_col','gscpi')}"
    if treat["rule"] == "custom_dates":
        custom_csv = cfg["paths"]["custom_events_csv"]
        treat_args += f" --custom_events {custom_csv}"

    if iv["spec"] == "peer_it_lagK":
        iv_args = f"--iv_spec peer_it_lagK --iv_lag {iv.get('lag',4)}"
    else:
        waves_csv = cfg["paths"]["industry_waves_csv"]
        iv_args = f"--iv_spec industry_wave --industry_wave_csv {waves_csv}"

    run(f"python -m src.features.compute_ccc --fin data/raw/fin.csv --gscpi {gscpi_csv} --it data/interim/it_index.csv --out data/processed/firm_quarter.csv {treat_args} {iv_args}")

    # 5) Models
    run("python -m src.models.fe_panel --data data/processed/firm_quarter.csv --out reports/tables/fe_main.csv")
    if iv["spec"] == "peer_it_lagK":
        run('python -m src.models.iv_panel --data data/processed/firm_quarter.csv --endog IT_lag1 --instr IV_peer_IT --out reports/tables/iv_main.txt')
    else:
        run('python -m src.models.iv_panel --data data/processed/firm_quarter.csv --endog IT_lag1 --instr IV_wave --out reports/tables/iv_main.txt')

    run("python -m src.models.did_eventstudy --data data/processed/firm_quarter.csv --out reports/tables/did_event.csv --fig reports/figures/eventstudy.png")
    run("python -m src.models.mediation_statistical --data data/processed/firm_quarter.csv --out reports/tables/mediation.csv")

    print('[OK] All done. See reports/ for outputs.')

if __name__ == '__main__':
    main()
