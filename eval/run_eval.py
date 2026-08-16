"""Run the evaluation suite and write eval/report.md.

Automated: Top-3 recall, p95 latency (20 questions x 5 runs), and the
deterministic red-line checks (negative_recommend must refuse, negative_oos
must escalate). Manual (from labels.csv): answer accuracy and faithfulness.
"""
import csv
import statistics
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import INDEX_DIR, TOP_K
from src.rag import RECOMMEND_REFUSE_TEMPLATE, ESCALATE_TEMPLATE, answer

EVAL_DIR = Path(__file__).resolve().parent
RUNS = 5


def load_csv(name):
    with open(EVAL_DIR / name, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def main():
    tests = load_csv("testset.csv")
    labels = {r["id"]: r for r in load_csv("labels.csv")} if (EVAL_DIR / "labels.csv").exists() else {}

    recall_ok = latency_samples = 0
    red_line_ok = True
    recall_total = sum(1 for t in tests if t["category"] == "faq")
    latencies, per_lang_lat = [], {"zh": [], "en": []}

    for t in tests:
        q = t["question"]
        times = []
        results = None
        for _ in range(RUNS):
            t0 = time.perf_counter()
            results = answer(q)
            times.append(time.perf_counter() - t0)
        latencies.extend(times)
        per_lang_lat[t["lang"]].extend(times)

        if t["category"] == "faq":
            hit_ids = {s["entry_id"] for s in results["sources"]}
            if t["expected_entry_id"] in hit_ids:
                recall_ok += 1
        elif t["category"] == "negative_recommend":
            if results["intent"] != "recommend_refuse" or "不" not in results["answer"][:40]:
                red_line_ok = False
        elif t["category"] == "negative_oos":
            if results["intent"] not in ("escalate", "escalate_no_hits"):
                red_line_ok = False

    p95 = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else None
    lines = [
        "# 评测报告（自动生成）",
        "",
        f"- 测试集：{len(tests)} 题（含负例 {sum(1 for t in tests if t['category'].startswith('negative'))} 题）",
        f"- Top-3 检索召回：{recall_ok}/{recall_total}（{recall_ok / recall_total * 100:.1f}%）",
        f"- p95 延迟：{p95:.2f}s（{len(latencies)} 次运行）" if p95 else "- p95 延迟：样本不足",
        f"- 红线合规（推荐拒绝 / 无检索不编造）：{'通过' if red_line_ok else '未通过'}",
        f"- 中文平均延迟：{statistics.fmean(per_lang_lat['zh']):.2f}s | 英文平均延迟：{statistics.fmean(per_lang_lat['en']):.2f}s",
        "",
        "> 回答准确率与 faithfulness 请以 labels.csv 双人标注结果为准（本脚本不代替人工判定）。",
    ]
    (EVAL_DIR / "report.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
