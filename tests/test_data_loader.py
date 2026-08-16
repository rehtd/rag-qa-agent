import pytest
from src.data_loader import parse_faq, load_faqs, FaqEntry
from src.config import DATA_DIR

SAMPLE = """---
q_zh: 测试问题？
a_zh: 测试答案。
q_en: Test question?
a_en: Test answer.
source: https://example.com
date: 2026-08-16
topic: 测试
"""

def test_parse_single_entry():
    entries = parse_faq(SAMPLE)
    assert len(entries) == 1
    e = entries[0]
    assert e.id == "faq-001"
    assert e.q_zh == "测试问题？"
    assert e.topic == "测试"

def test_missing_field_raises():
    bad = SAMPLE.replace("topic: 测试", "")
    with pytest.raises(ValueError, match="topic"):
        parse_faq(bad)

def test_multiline_value_continuation():
    text = SAMPLE.replace(
        "a_zh: 测试答案。",
        "a_zh: 第一行\n  第二行。",
    )
    e = parse_faq(text)[0]
    assert e.a_zh == "第一行 第二行。"

def test_load_faqs_reads_data_file():
    entries = load_faqs(DATA_DIR)
    assert len(entries) >= 3
    assert all(isinstance(e, FaqEntry) for e in entries)
