"""Retrieve + generate with citations via LangChain (DeepSeek OpenAI-compatible API)."""
import os
import re
import time

from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI

from src.config import (
    COLLECTION_NAME, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL, EMBED_MODEL,
    INDEX_DIR, MODELS_CACHE, RETRIEVAL_MAX_DISTANCE, TOP_K,
)
from src.router import route

DISCLAIMER = "（演示用途：信息整理自香港官方消费者教育资料，可能过时，以官网为准；不构成投资建议。）"
DISCLAIMER_EN = (
    "For demonstration only: information compiled from official HK consumer-education "
    "materials, may be outdated; refer to official sources; not investment advice."
)
ESCALATE_TEMPLATE = (
    "抱歉，这个问题建议联系银行或相关机构人工处理。香港金管局公众查询热线：(852) 2878 1111，"
    "或访问 https://www.hkma.gov.hk 提交查询。"
)
RECOMMEND_REFUSE_TEMPLATE = (
    "抱歉，我不能提供个性化的产品推荐或投资建议。请咨询持牌机构（银行、保险公司或证监会持牌中介），"
    "或先阅读官方教育资料了解基本概念。"
)
CHAT_TEMPLATE = (
    "你好！我可以回答香港金融消费者相关的常见问题（开户、收费、转账、理财科普等），"
    "请问有什么可以帮你？"
)

PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", (
            "你是一名金融消费者教育问答助手。请仅根据以下官方资料回答问题，并在句末标注来源编号，如 [1]。"
            "规则：1) 资料不足以回答时，直接回复转人工话术，不得编造；"
            "2) 不得给出个性化产品推荐或投资建议；3) 回答末尾附免责声明。"
            "4) 若资料中出现金额数字，回答中的金额必须逐字原样引用该数字；"
            "5) 除非检索结果为空，禁止出现「资料未说明」「未列出」「未涵盖」等否认资料内容的表述——资料写了什么就答什么；"
            "6) 必须用与用户提问相同的语言回答（中文问中文答，英文问英文答）；"
            "7) 不得在回答中附加转人工话术（转人工由系统路由处理，与生成无关）。\n\n"
            "官方资料：\n{context}\n\n用户问题：{question}"
        )),
    ]
)


def _llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=DEEPSEEK_MODEL,
        api_key=os.environ["DEEPSEEK_API_KEY"],
        base_url=DEEPSEEK_BASE_URL,
        temperature=0,
    )


def _embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        cache_folder=str(MODELS_CACHE),
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def _filter_by_distance(scored, max_distance=RETRIEVAL_MAX_DISTANCE) -> list[dict]:
    out = []
    for doc, score in scored:
        if score > max_distance:
            continue
        out.append({
            "doc": doc.page_content,
            "entry_id": doc.metadata["entry_id"],
            "lang": doc.metadata["lang"],
            "source": doc.metadata["source"],
            "topic": doc.metadata.get("topic", ""),
        })
    return out


def retrieve(question: str, embeddings=None, top_k: int = TOP_K) -> list[dict]:
    store = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=str(INDEX_DIR),
        embedding_function=embeddings or _embeddings(),
    )
    scored = store.similarity_search_with_score(question, k=top_k)
    return _filter_by_distance(scored)


def build_prompt(question: str, hits: list[dict]) -> str:
    context = "\n".join(
        f"[{i}] {h['doc']}（来源：{h['source']}，主题：{h['topic']}）"
        for i, h in enumerate(hits, 1)
    )
    return PROMPT.format(context=context, question=question)


def answer(question: str, llm=None, embeddings=None) -> dict:
    decision = route(question)
    if decision.intent == "recommend_refuse":
        return {"answer": RECOMMEND_REFUSE_TEMPLATE, "sources": [], "intent": "recommend_refuse"}
    if decision.intent == "escalate":
        return {"answer": ESCALATE_TEMPLATE, "sources": [], "intent": "escalate"}
    if decision.intent == "chat":
        return {"answer": CHAT_TEMPLATE, "sources": [], "intent": "chat"}

    llm = llm or _llm()
    hits = retrieve(question, embeddings)
    if not hits:
        return {"answer": ESCALATE_TEMPLATE, "sources": [], "intent": "escalate_no_hits"}

    prompt_text = build_prompt(question, hits)
    t0 = time.perf_counter()
    resp = llm.invoke(prompt_text)
    latency_s = time.perf_counter() - t0
    text = resp.content.strip()
    disclaimer = DISCLAIMER_EN if not re.search(r"[\u4e00-\u9fff]", question) else DISCLAIMER
    if disclaimer not in text:
        text = f"{text}\n\n{disclaimer}"
    sources = [{"entry_id": h["entry_id"], "source": h["source"], "topic": h["topic"]} for h in hits]
    return {"answer": text, "sources": sources, "intent": "faq", "latency_s": latency_s}
