
# 一鍵在私有環境跑完整流程

## 步驟
1. 準備受限資料（不公開）：
   - `data/private/compustat_fundq.csv`
   - `data/private/10k_raw/`（10-K 原始檔）
2. （可選）準備：
   - `data/raw/it_labels.csv`（監督式 IT 指標標註；可參考 `docs/templates/it_labels_template.csv`）
   - `data/raw/external/industry_waves.csv`（IV 波次；參考 `docs/templates/industry_waves_template.csv`）
   - `data/raw/external/event_dates.csv`（自定義事件期；參考 `docs/templates/event_dates_template.csv`）
3. 編輯 `config/config.yaml`（設定 treat/IV 規則與路徑）。
4. 執行：
   ```bash
   bash scripts/run_private.sh
   # 或 Windows：scripts\run_private.bat
   ```
5. 看結果：`reports/`（表格 csv/txt 與圖）。

## 常見問題
- 欄位/格式錯誤：先跑 `make validate` 看錯在哪一欄。
- 沒有 it_labels.csv：把 `run.train_it` 改成 `false`，會改用關鍵詞代理。
- 想用自有衝擊變數：把 `config.yaml` 的 `treat.shock_col` 指到你的欄位，再把它 merge 到 `data/raw/external/*.csv` 裡即可。
