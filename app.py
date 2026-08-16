import streamlit as st

from src.config import DATA_DIR
from src.rag import DISCLAIMER, answer

st.set_page_config(page_title="香港金融消费者问答助手", page_icon="💬")
st.title("香港金融消费者问答助手")
st.caption("演示项目 · 信息整理自 IFEC / HKMA 公开教育资料 · 中英双语")

question = st.text_input("请输入你的问题（例：在香港开银行账户要什么文件？）", key="q")
if st.button("提问") and question.strip():
    with st.spinner("检索中…"):
        result = answer(question.strip())
    st.markdown("**回答**")
    st.markdown(result["answer"])
    if result["sources"]:
        st.markdown("**来源**")
        for i, s in enumerate(result["sources"], 1):
            st.markdown(f"{i}. {s['source']}（主题：{s['topic']}）")

st.markdown("---")
st.caption(DISCLAIMER)
