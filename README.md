# 香港金融消费者双语问答助手

基于香港官方消费者教育资料的中英双语 RAG 问答演示项目（作品集项目）。

## 功能
- 中英双语问答，回答带来源编号与链接
- 四分类意图路由：FAQ / 闲聊 / 推荐类拒绝 / 转人工
- 评测：held-out 测试集，召回 / 准确率 / faithfulness / p95 延迟 / 编造率=0

## 快速开始
（Windows）
1. `python -m venv .venv`
2. `$env:HF_ENDPOINT = "https://hf-mirror.com"`（模型下载镜像）
3. `.venv/Scripts/python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`
4. 复制 `.env.example` 为 `.env` 并填入 `DEEPSEEK_API_KEY`
5. `.venv/Scripts/python scripts/build_index.py`
6. `.venv/Scripts/python -m streamlit run app.py`

## 数据
见 `data/README.md`（来源、授权、声明）。

## 评测
见 `eval/README`（运行方式与指标定义）。

## 密钥安全
- `.env` 不入库（.gitignore 已排除）。
- 若误提交：立即到 DeepSeek 平台 revoke 该 key → 更换新 key → `git filter-repo` 或重建仓库清除历史。
