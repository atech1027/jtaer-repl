
# Evidence Index (GitHub Release)

> 本資料夾提供**論文證據檔（可公開）**的「凍結版本」。目前內容為 **Demo** 跑出的樣本，
> 你在私有環境重跑後，只需覆蓋本資料夾即可（或執行 `make release` 自動更新）。

## Tables
- `tables/fe_main.csv` / `fe_main.tex`：固定效果主回歸結果
- `tables/iv_main.txt`：IV（2SLS/備援版）估計輸出
- `tables/did_event.csv` / `did_event.tex`：事件研究係數（相對期）
- `tables/mediation.csv` / `mediation.tex`：中介統計分解（非因果）

## Figures
- `figures/eventstudy.png`：事件研究圖（含 95% CI）

## Data (shareable)
- `data/firm_quarter.csv`：處理後的公司×季面板（Demo 版）。
  - 你的正式版本：請在私有環境依 `docs/REPLICATION.md` 重建後，以 `make release` 更新。

---

### 如何用私有資料更新本資料夾（Release）
1) 在私有環境按 `docs/TUTORIAL_ZH.md` 跑完整流程（或 `scripts/run_private.sh`）。  
2) 執行：
   ```bash
   make release
   ```
3) 將 `artifacts/` 整個資料夾提交到 GitHub，即可對外提供**可引用的證據檔**。

> 注意：請勿將 `data/private/**` 或任何授權受限的**原始**檔案提交到 GitHub。
