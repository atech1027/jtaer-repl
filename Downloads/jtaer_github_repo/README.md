
# JTAER 實證研究：IT × 供應鏈衝擊 × 工作資本（可再現套件）

可直接丟到 GitHub 的完整專案骨架：含 **IV / DiD / 事件研究 / 中介分解（統計）** 腳本、CI、pre-commit、測試，以及**合成資料 demo**，不含任何專有資料。

## 快速開始
```bash
conda env create -f environment.yml
conda activate jtaer-repl
make demo         # 跑完整 demo（合成資料）
make model        # 主回歸（FE）
make iv           # 工具變數（2SLS）
make did          # DiD + 事件研究
make event_plot   # 畫事件研究圖
make mediation    # 中介統計分解（非因果）
make test         # 單元測試
```

## 結構
```
data/
  raw/            # 放原始資料（不版控）；已含合成示例
  interim/
  processed/
docs/
reports/          # 圖與表
src/
  text/           # IT 指標（10-K 文本示例）
  features/       # 變數計算與併表
  models/         # FE / IV / DiD / 事件研究 / 中介
  utils/          # I/O、合成資料
tests/
.github/workflows # CI
```

## 注意
- 此套件僅示範流程與介面；**IV 與中介分析僅供模板，請依你的識別策略與資料替換與審核**。
- 真實資料放入 `data/raw/` 後，執行 `make all` 或 `dvc repro`（如使用 DVC）。


## 在私有資料上「一鍵」跑
1) 把受限資料放到 `data/private/`（見 `docs/TUTORIAL_ZH.md`）。
2) 編輯 `config/config.yaml`。
3) 執行：
```bash
bash scripts/run_private.sh   # 或 Windows: scripts\run_private.bat
```


## 發布（Artifacts）
要把**論文證據檔**一併放上 GitHub：
1) 在本地或私有環境跑完整流程（`make demo`、`bash scripts/run_private.sh` 或 `bash scripts/run_public.sh`）。
2) 執行：
```bash
make release
```
3) 版本庫中的 `artifacts/` 會包含可公開的**最終表格、圖檔與處理後面板**。直接 commit & push 即可。
