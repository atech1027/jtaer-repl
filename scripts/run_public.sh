
#!/usr/bin/env bash
set -euo pipefail
# 1) Fetch public data
python -m src.data.fetch_fin_from_sec --tickers_csv docs/templates/tickers_template.csv --out data/raw/fin.csv
python -m src.data.download_gscpi --out data/raw/external/gscpi.csv
# 2) Build IT index (uses existing 10-K demo texts unless you add your own)
python -m src.text.build_it_index --input data/raw/10k --output data/interim/it_index.csv
# 3) Build panel
python -m src.features.compute_ccc --fin data/raw/fin.csv --gscpi data/raw/external/gscpi.csv --it data/interim/it_index.csv --out data/processed/firm_quarter.csv
# 4) Models
python -m src.models.fe_panel --data data/processed/firm_quarter.csv --out reports/tables/fe_main.csv
python -m src.models.iv_panel --data data/processed/firm_quarter.csv --endog IT_lag1 --instr IV_peer_IT --out reports/tables/iv_main.txt
python -m src.models.did_eventstudy --data data/processed/firm_quarter.csv --out reports/tables/did_event.csv --fig reports/figures/eventstudy.png
python -m src.models.mediation_statistical --data data/processed/firm_quarter.csv --out reports/tables/mediation.csv
# 5) Freeze
python -m scripts.freeze_artifacts
echo "[OK] Public run complete. See artifacts/"
