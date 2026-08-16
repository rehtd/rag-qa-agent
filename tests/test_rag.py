from src.rag import answer, build_prompt, DISCLAIMER

class FakeLlm:
    def __init__(self, text):
        self._text = text

    def invoke(self, prompt):
        msg = type("M", (), {})()
        msg.content = self._text
        return msg

def _fake_hits():
    return [
        {"doc": "开户需要身份证和住址证明。", "entry_id": "faq-001", "lang": "zh",
         "source": "演示自编", "topic": "开户"},
    ]

def test_recommend_refused_without_calling_llm():
    r = answer("帮我选一只基金", llm=object(), embeddings=object())
    assert r["intent"] == "recommend_refuse"
    assert "不能提供个性化的产品推荐" in r["answer"]

def test_escalate_without_calling_llm():
    r = answer("我要投诉", llm=object(), embeddings=object())
    assert r["intent"] == "escalate"
    assert "2878 1111" in r["answer"]

def test_build_prompt_has_citations_and_rules():
    p = build_prompt("开户要什么文件", _fake_hits())
    assert "[1]" in p
    assert "不得编造" in p
    assert "开户要什么文件" in p

def test_answer_appends_disclaimer_when_missing(monkeypatch):
    monkeypatch.setattr("src.rag.route", lambda q: __import__("src.router", fromlist=["RouteDecision"]).RouteDecision("faq"))
    monkeypatch.setattr("src.rag.retrieve", lambda *a, **k: _fake_hits())
    monkeypatch.setattr("src.rag._llm", lambda: FakeLlm("这是回答。"))
    r = answer("开户要什么文件")
    assert r["intent"] == "faq"
    assert DISCLAIMER in r["answer"]
    assert r["sources"][0]["entry_id"] == "faq-001"

def test_no_hits_escalates(monkeypatch):
    monkeypatch.setattr("src.rag.route", lambda q: __import__("src.router", fromlist=["RouteDecision"]).RouteDecision("faq"))
    monkeypatch.setattr("src.rag.retrieve", lambda *a, **k: [])
    r = answer("火星上怎么开户", llm=object())
    assert r["intent"] == "escalate_no_hits"

def test_filter_by_distance_drops_unrelated():
    from src.rag import _filter_by_distance

    class D:
        def __init__(self):
            self.page_content = "x"
            self.metadata = {"entry_id": "faq-001", "lang": "zh", "source": "s", "topic": "t"}

    kept = _filter_by_distance([(D(), 0.3), (D(), 0.9)])
    assert len(kept) == 1
    assert kept[0]["entry_id"] == "faq-001"
