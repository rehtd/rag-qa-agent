from src.router import route

def test_recommend_keywords_refused():
    for q in ["帮我选一只基金", "买哪个保险好", "该不该买股票", "should I buy this fund"]:
        assert route(q).intent == "recommend_refuse"

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
