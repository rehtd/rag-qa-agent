from src.router import route

def test_recommend_keywords_refused():
    for q in ["帮我选一只基金", "买哪个保险好", "该不该买股票", "should I buy this fund"]:
        assert route(q).intent == "recommend_refuse"


def test_n01_bang_wo_tiao_is_recommend_refuse():
    assert route("我月薪两万，帮我挑一只基金").intent == "recommend_refuse"

def test_escalate_keywords():
    for q in ["我要投诉", "转人工", "打客服电话"]:
        assert route(q).intent == "escalate"

def test_chat_greetings():
    for q in ["你好", "hi", "谢谢"]:
        assert route(q).intent == "chat"

def test_default_faq():
    for q in ["在香港开银行账户要什么文件", "什么是存款保障", "what is diversification"]:
        assert route(q).intent == "faq"

def test_empty_input_is_chat():
    assert route("  ").intent == "chat"


def test_english_keywords_use_word_boundaries():
    assert route("Why do advisers warn against putting everything into a single investment?").intent == "faq"
    assert route("Is there an official body I can turn to if my bank ignores my complaint?").intent == "faq"
    assert route("I want to complain about my bank").intent == "escalate"
    assert route("我要投诉").intent == "escalate"
