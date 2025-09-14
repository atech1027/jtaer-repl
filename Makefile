
.PHONY: all demo data features model iv did event_plot mediation lint format test clean

all: data features model iv did event_plot mediation

demo:
	python -m src.utils.make_synthetic --out data/raw
	python -m src.text.build_it_index --input data/raw/10k --labels_csv data/raw/it_labels.csv --output data/interim/it_index.csv --eval_dir reports/tables
	python -m src.features.compute_ccc --fin data/raw/fin.csv --gscpi data/raw/external/gscpi.csv --it data/interim/it_index.csv --out data/processed/firm_quarter.csv
	python -m src.models.fe_panel --data data/processed/firm_quarter.csv --out reports/tables/fe_main.csv
	python -m src.models.iv_panel --data data/processed/firm_quarter.csv --out reports/tables/iv_main.csv
	python -m src.models.did_eventstudy --data data/processed/firm_quarter.csv --out reports/tables/did_event.csv --fig reports/figures/eventstudy.png
	python -m src.models.mediation_statistical --data data/processed/firm_quarter.csv --out reports/tables/mediation.csv

data:
	python -m src.text.build_it_index --input data/raw/10k --labels_csv data/raw/it_labels.csv --output data/interim/it_index.csv --eval_dir reports/tables

features:
	python -m src.features.compute_ccc --fin data/raw/fin.csv --gscpi data/raw/external/gscpi.csv --it data/interim/it_index.csv --out data/processed/firm_quarter.csv

model:
	python -m src.models.fe_panel --data data/processed/firm_quarter.csv --out reports/tables/fe_main.csv

iv:
	python -m src.models.iv_panel --data data/processed/firm_quarter.csv --out reports/tables/iv_main.csv

did:
	python -m src.models.did_eventstudy --data data/processed/firm_quarter.csv --out reports/tables/did_event.csv --fig reports/figures/eventstudy.png

event_plot:
	python -m src.models.did_eventstudy --data data/processed/firm_quarter.csv --fig reports/figures/eventstudy.png

mediation:
	python -m src.models.mediation_statistical --data data/processed/firm_quarter.csv --out reports/tables/mediation.csv

lint:
	ruff check .

format:
	ruff check --fix . && ruff format .

test:
	pytest -q

clean:
	rm -rf data/interim/* data/processed/* reports/tables/* reports/figures/*


prepare_compustat:
	python -m src.data.prepare_fin_compustat --input data/private/compustat_fundq.csv --out data/raw/fin.csv

prepare_10k:
	python -m src.data.prepare_10k_sec --input_dir data/private/10k_raw --out_dir data/raw/10k

validate:
	python -m src.features.validate --fin data/raw/fin.csv --gscpi data/raw/external/gscpi.csv


it_train:
	python -m src.text.build_it_index --input data/raw/10k --labels_csv data/raw/it_labels.csv --output data/interim/it_index.csv --eval_dir reports/tables

iv_wave_demo:
	python -m src.features.compute_ccc --fin data/raw/fin.csv --gscpi data/raw/external/gscpi.csv --it data/interim/it_index.csv --out data/processed/firm_quarter.csv --iv_spec industry_wave --industry_wave_csv data/raw/external/industry_waves.csv



release:
	python -m scripts.freeze_artifacts
