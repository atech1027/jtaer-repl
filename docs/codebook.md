
# 變數字典（示例）
| 變數 | 單位 | 說明 |
|---|---|---|
| firm_id | str | 公司識別碼（唯一） |
| quarter | str (YYYYQ) | 季度 |
| industry | str | 行業（NAICS2 示意） |
| sales | USD | 銷售收入（期間） |
| cogs | USD | 銷貨成本（期間） |
| inventory | USD | 期末存貨（存量） |
| receivables | USD | 期末應收帳款（存量） |
| payables | USD | 期末應付帳款（存量） |
| CCC | days | 現金週轉天數 |
| DIO | days | 存貨週轉天數 |
| DSO | days | 應收帳款週轉天數 |
| DPO | days | 應付帳款週轉天數 |
| IT_index | z-score | IT/電商指標（10-K 文本示例） |
| gscpi | z-score | 供應鏈壓力指數 |
| treat | 0/1 | 事件研究示例處理指標（門檻化 gscpi） |
| event_time | int | 相對事件期（示例） |

| IT_index_source | str | 來源說明（supervised / keywords） |
| treat | 0/1 | 處理指標（依 `--treat_rule` 定義） |
| event_time | int | 相對事件期 |
| IV_peer_IT / IV_wave | var | 工具變數欄位（依 `--iv_spec` 定義） |
