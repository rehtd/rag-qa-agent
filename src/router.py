"""Rule-first intent routing. Four intents: faq | chat | recommend_refuse | escalate."""
from dataclasses import dataclass

RECOMMEND_KEYWORDS = [
    "帮我选", "帮我挑", "推荐", "买哪个", "买什么", "买哪只", "该不该买", "应不应该买",
    "哪个好", "哪只基金", "哪款保险", "建议我买", "适合我吗", "选哪",
    "recommend", "which fund", "which insurance", "should i buy", "best for me",
]
ESCALATE_KEYWORDS = ["人工", "客服电话", "转人工", "投诉", "complain", "human agent", "hotline"]
CHAT_GREETINGS = ["你好", "您好", "hi", "hello", "谢谢", "thank", "在吗", "你是谁", "who are you"]

@dataclass
class RouteDecision:
    intent: str

def route(question: str) -> RouteDecision:
    q = question.strip().lower()
    if not q:
        return RouteDecision("chat")
    if any(k in q for k in RECOMMEND_KEYWORDS):
        return RouteDecision("recommend_refuse")
    if any(k in q for k in ESCALATE_KEYWORDS):
        return RouteDecision("escalate")
    if any(k in q for k in CHAT_GREETINGS):
        return RouteDecision("chat")
    return RouteDecision("faq")
