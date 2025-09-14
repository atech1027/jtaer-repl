
# Replication Guide (with Licensed Data)

## TL;DR
1. 申請並下載受限資料至 `data/private/`：
   - `compustat_fundq.csv`
   - `10k_raw/` （10-K 原始檔案資料夾，txt/html/htm 皆可）
2. 轉換為公開架構：
   ```bash
   python -m src.data.prepare_fin_compustat --input data/private/compustat_fundq.csv --out data/raw/fin.csv
   python -m src.data.prepare_10k_sec --input_dir data/private/10k_raw --out_dir data/raw/10k
   python -m src.features.validate --fin data/raw/fin.csv --gscpi data/raw/external/gscpi.csv
   ```
3. 跑完整分析：
   ```bash
   make all
   ```

## Column Contract
最終必需表：`data/raw/fin.csv`
```
firm_id, quarter(YYYYQ), industry(optional), sales, cogs, inventory, receivables, payables
```
外部衝擊：`data/raw/external/gscpi.csv`
```
quarter, gscpi
```

## 參數化欄位名稱
若你的 Compustat 匯出欄位不同，可透過參數覆寫：
```
python -m src.data.prepare_fin_compustat --input ... --out data/raw/fin.csv   --firm_id_col gvkey --date_col datadate --sales_col saleq --cogs_col cogsq   --inventory_col invtq --receivables_col rectq --payables_col apq --industry_col naics
```

## 注意事項
- 本 repo 僅包含**派生表**與程式，`data/private/**` 永不提交版本庫。
- 如需匿名化或脫敏的可分享樣本，可在 `data/processed/` 層級再行聚合/抽樣/加噪，但請確認不違反授權合約。


## IT Index (Supervised)
1) 準備標註表 `data/raw/it_labels.csv`（欄位：`firm_id,year,label`；可加 `text` 欄以覆蓋檔案內容）。
2) 產出 IT 指標並輸出評估度量（F1、混淆矩陣）：
```bash
python -m src.text.build_it_index --input data/raw/10k \
  --labels_csv data/raw/it_labels.csv \
  --output data/interim/it_index.csv \
  --eval_dir reports/tables
```
輸出：
- `reports/tables/it_eval.csv`
- `reports/tables/it_confusion_matrix.csv`
- `reports/tables/it_classification_report.txt`
