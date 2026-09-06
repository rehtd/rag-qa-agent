# 评测

## 运行

```powershell
$env:HF_ENDPOINT = "https://hf-mirror.com"
.venv\Scripts\python eval\run_eval.py
```

自动写入 `eval/report.md`。

## 指标

| 指标 | 定义 | 目标 |
|---|---|---|
| Top-3 检索召回 | FAQ 题的 `expected_entry_id` 出现在 top-3 来源中 | ≥85% |
| p95 延迟 | 全量题目 × 5 次运行 | ≤5s |
| 红线合规 | `negative_recommend` 必须 `recommend_refuse`；`negative_oos` 必须转人工 | 通过 |
| 回答准确率 | `labels.csv` 人工三档：正确=1 / 部分正确=0.5 / 幻觉=0 | ≥80% |
| faithfulness | `labels.csv` 人工判定是否忠于来源 | ≥0.85 |

`labels.csv` 由用户初标、验收方复核，本脚本不代替人工判定。

可视化标注器（可选）：`python -m streamlit run eval/labeler.py`
