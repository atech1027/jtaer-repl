
# Data Availability & Licensing

本研究使用之部份資料（如 **Compustat FUNDQ/WRDS** 或 **Bureau van Dijk Orbis**）受授權限制，**無法直接隨附或公開再散佈**。為兼顧可重現性與授權遵循，我們提供以下層級：

## 1) 開源層（本 repo 已包含）
- **合成示例資料**與完整程式碼（`make demo` 可直接重建主要表與圖）。
- 完整管線、測試、與文件。

## 2) 受限重建層（需要讀者自行取得授權）
- 取得 Compustat/Orbis 等授權後，將原始匯出置於：`data/private/`（此路徑已被 `.gitignore` 排除）。
- 執行準備腳本將受限資料轉換為公開架構：
  ```bash
  # Compustat FUNDQ 轉換成 data/raw/fin.csv（可用參數調整欄位名稱）
  python -m src.data.prepare_fin_compustat --input data/private/compustat_fundq.csv --out data/raw/fin.csv

  # 本地 10-K 檔案（txt/html）清成純文字，寫入 data/raw/10k/
  python -m src.data.prepare_10k_sec --input_dir data/private/10k_raw --out_dir data/raw/10k

  # 驗證欄位結構
  python -m src.features.validate --fin data/raw/fin.csv --gscpi data/raw/external/gscpi.csv
  ```
- 之後即可用 `make all` 產生完整結果。

## 3) 申請流程（建議寫在論文資料附註）
- **Compustat/WRDS**：讀者可向其機構圖書館或學術單位申請 WRDS 帳號與資料存取，依自身合約下載 FUNDQ 表，欄位至少包含：`gvkey, datadate, saleq, cogsq, invtq, rectq, apq, (naics)`。
- **10-K/SEC**：10-K 屬公開檔，但如使用第三方整理檔，請遵循該供應商授權；或由讀者自行以 SEC EDGAR 抓取並以本 repo 之清理腳本轉為純文字。

## 4) 我們不會公開的內容
- 任何原始微觀資料（`data/private/**`）
- 任何具身分可識別或受合約限制之欄位

## 5) 學術引用與複製研究
- 請引用本 repo（見 `CITATION.cff`），並在再現研究中說明你所使用之授權來源與版本。


### IT 指標標註
- 若標註文本受授權限制，請放在 `data/private/`，由你方持有；再以 `data/raw/it_labels.csv` 存放**僅包含識別與標註**的可分享表（必要時可匿名化）。
- 程式會從 `data/raw/10k/*.txt` 讀取對應文本內容。
