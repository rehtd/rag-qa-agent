"""可视化标注器：为 eval/testset.csv 每道题生成系统回答，用户打分并写回 eval/labels.csv。

- 准确率三档：正确=1 / 部分正确=0.5 / 幻觉=0
- faithfulness 二档：忠于来源=1 / 不忠于来源=0
- 负例（negative_*）的「正确」指系统行为合规（拒绝推荐 / 转人工）；faithfulness 按是否编造判定。
- 每次打分/翻页即时写盘，可随时中断续标。

运行：python -m streamlit run eval/labeler.py --server.port 8503（用项目 venv 的 python）
"""
import csv
import sys
from pathlib import Path

import streamlit as st

EVAL_DIR = Path(__file__).resolve().parent
APP_ROOT = EVAL_DIR.parent
sys.path.insert(0, str(APP_ROOT))

from src.config import DATA_DIR  # noqa: E402
from src.data_loader import load_faqs  # noqa: E402
from src.rag import _embeddings, _llm, answer  # noqa: E402

LABEL_FILE = EVAL_DIR / "labels.csv"
COLS = ["id", "user_label", "ai_label", "final_label", "user_faithfulness", "ai_faithfulness", "notes"]

ACC_OPTIONS = {"正确（1）": "1", "部分正确（0.5）": "0.5", "幻觉（0）": "0"}
FAITH_OPTIONS = {"忠于来源（1）": "1", "不忠于来源（0）": "0"}


@st.cache_resource
def _faq_map():
    return {e.id: e for e in load_faqs(DATA_DIR)}


@st.cache_resource
def _resources():
    return _llm(), _embeddings()


@st.cache_data(show_spinner=False)
def _run(question: str) -> dict:
    llm, emb = _resources()
    return answer(question, llm=llm, embeddings=emb)


def load_tests():
    with open(EVAL_DIR / "testset.csv", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def load_labels() -> dict:
    rows = {}
    if LABEL_FILE.exists():
        with open(LABEL_FILE, encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                rows[r["id"]] = r
    return rows


def save_labels(test_ids, rows, drafts):
    merged = {}
    for tid in test_ids:
        m = {"id": tid}
        m.update(rows.get(tid, {}))
        m.update(drafts.get(tid, {}))
        merged[tid] = m
    with open(LABEL_FILE, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        for tid in test_ids:
            w.writerow({c: merged[tid].get(c, "") for c in COLS})


st.set_page_config(page_title="评测标注器", page_icon="🏷️")
st.title("评测标注器")
st.caption("23 题 · 准确率三档（1/0.5/0）+ faithfulness 二档（1/0）· 打分与翻页即时写入 labels.csv")

tests = load_tests()
test_ids = [t["id"] for t in tests]
rows = load_labels()

if "idx" not in st.session_state:
    st.session_state.idx = 0
if "drafts" not in st.session_state:
    st.session_state.drafts = {}

idx = st.session_state.idx
t = tests[idx]
tid = t["id"]
draft = st.session_state.drafts.setdefault(
    tid,
    {
        "user_label": rows.get(tid, {}).get("user_label", ""),
        "user_faithfulness": rows.get(tid, {}).get("user_faithfulness", ""),
        "notes": rows.get(tid, {}).get("notes", ""),
    },
)

# 进度条
done = sum(1 for x in test_ids if st.session_state.drafts.get(x, {}).get("user_label"))
st.progress(done / len(test_ids))
st.write(f"已标注 **{done}/{len(test_ids)}** 题（当前第 {idx + 1} 题）")

# 当前题与系统回答
st.markdown(f"### #{idx + 1} · `{tid}`（lang: {t['lang']}）")
st.markdown(f"**问题**：{t['question']}")
st.caption(f"类别：{t['category']} ｜ 期望条目：{t['expected_entry_id'] or '（负例，无期望条目）'}")
if t["category"].startswith("negative"):
    st.info("负例：『正确』指系统行为合规（拒绝推荐或转人工）；faithfulness 按是否出现编造判定。")

with st.spinner("生成回答中…"):
    r = _run(t["question"])
st.markdown(f"**系统回答**（intent: `{r['intent']}`）")
st.markdown(r["answer"])
if r["sources"]:
    st.markdown("**来源（已展开原文，直接对照判 faithfulness）**")
    faq_map = _faq_map()
    seen = set()
    for i, s in enumerate(r["sources"], 1):
        eid = s["entry_id"]
        if eid in seen:
            continue
        seen.add(eid)
        e = faq_map.get(eid)
        if e is None:
            st.markdown(f"{i}. `{eid}` ｜ {s['source']}（主题：{s['topic']}）—（未找到条目原文）")
            continue
        q = e.q_zh if t["lang"] == "zh" else e.q_en
        a = e.a_zh if t["lang"] == "zh" else e.a_en
        with st.expander(f"{i}. `{eid}` ｜ {s['source']}（主题：{s['topic']}）", expanded=True):
            st.markdown(f"**问题**：{q}")
            st.markdown(f"**答案**：{a}")
            st.caption(f"收录日期：{e.date}")
else:
    st.caption("（无来源引用）")

st.markdown("---")
st.markdown("**打分**")

acc_index = None
if draft["user_label"] in ACC_OPTIONS.values():
    acc_index = list(ACC_OPTIONS.values()).index(draft["user_label"])
acc = st.radio("准确率", list(ACC_OPTIONS.keys()), index=acc_index, key=f"acc_{tid}", horizontal=True)
if acc and draft["user_label"] != ACC_OPTIONS[acc]:
    draft["user_label"] = ACC_OPTIONS[acc]
    save_labels(test_ids, rows, st.session_state.drafts)

faith_index = None
if draft["user_faithfulness"] in FAITH_OPTIONS.values():
    faith_index = list(FAITH_OPTIONS.values()).index(draft["user_faithfulness"])
faith = st.radio("faithfulness（回答是否忠于来源/是否编造）", list(FAITH_OPTIONS.keys()), index=faith_index, key=f"faith_{tid}", horizontal=True)
if faith and draft["user_faithfulness"] != FAITH_OPTIONS[faith]:
    draft["user_faithfulness"] = FAITH_OPTIONS[faith]
    save_labels(test_ids, rows, st.session_state.drafts)

notes = st.text_input("备注（可选）", value=draft["notes"], key=f"notes_{tid}")
if notes != draft["notes"]:
    draft["notes"] = notes
    save_labels(test_ids, rows, st.session_state.drafts)

st.markdown("---")
c1, c2, c3 = st.columns([1, 1, 3])
if c1.button("⬅ 上一题", disabled=idx == 0, use_container_width=True):
    st.session_state.idx -= 1
    st.rerun()
if c2.button("下一题 ➡", disabled=idx == len(test_ids) - 1, use_container_width=True):
    st.session_state.idx += 1
    st.rerun()
c3.caption("翻页/打分均即时保存；刷新页面进度不丢失。")

with st.expander("标注进度汇总"):
    summary = []
    for tid2 in test_ids:
        d = st.session_state.drafts.get(tid2, {})
        summary.append(f"- `{tid2}`：acc={d.get('user_label') or '未标'} · faith={d.get('user_faithfulness') or '未标'}")
    st.markdown("\n".join(summary))
    st.caption("DSH 复核后填 ai_label / ai_faithfulness / final_label 列。")
