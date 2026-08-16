# AGENTS.md — 本项目执行指导（Cursor 每次会话自动读取）

> 你的角色：**执行工程师**。设计、需求、验收都不归你管。按本文件和实施计划逐条执行，不要自由发挥。

## 1. 开工必读（按顺序，用 read 工具读完再动手）

1. 设计文档（需求规格，只读不写）：
   `E:\Data\DSHWorkSpace\LearnWork\docs\superpowers\specs\2026-08-15-financial-consumer-qa-assistant-design.md`
2. 实施计划（任务清单，只读不写）：
   `E:\Data\DSHWorkSpace\LearnWork\docs\superpowers\plans\2026-08-15-financial-consumer-qa-assistant.md`

## 2. 工作流

- 严格按实施计划的 **Task 1 → Task 10** 顺序执行；每个 Task 内按 Step 逐条执行；
- 每个 Task 结束前：运行计划里写的命令/测试，**核对输出与 Expected 一致**，然后按计划里写的提交信息 `git commit`；
- 声称"完成"时必须附上**命令输出原文**（没有输出 = 没完成）；
- 每完成一个 Task，停下来向用户报告，等用户确认后再进下一个 Task（用户说"继续"才继续）；
- 每个 Task 的完成报告**同时追加**到 `E:\Data\DSHWorkSpace\LearnWork\project1\STATUS.md` 的「Cursor 完成报告」小节（只追加、不改写历史）。

## 3. 硬规则（违反 = 返工）

- 技术栈、目录结构、数据格式、指标口径一律以设计文档与实施计划为准，**不得更改**；
- 任何计划外的偏离（换库、改结构、跳步）必须先停手说明理由，等用户转达验收方确认；
- 禁止提交：`.env`、`models_cache/`、`data_snapshots/`、任何密钥（.gitignore 已配置，提交前自查 `git status`）；
- 禁止修改 `docs/superpowers/` 下的设计文档与实施计划；
- **数据边界**：`data/faq.txt` 里的条目由用户提供、验收方复核。你只做解析、索引和代码，**禁止自行编造金融条目内容**；只允许为调试临时添加标注为 `调试用` 的条目，提交前删除；
- **数据文件保护**：`data/faq.txt` 的最终数据集（42 条，含官方来源与自编条目）由验收方提供。若该文件已存在且条目数多于计划里 Task 2 的示例 3 条，**不得覆盖、不得删除、不得改写条目内容**，直接使用即可；
- 禁止添加计划之外的依赖；禁止顺手重构；YAGNI。

## 4. 环境须知（Windows）

- 用项目的 venv：`.venv\Scripts\python`；
- pip 安装一律加 `-i https://pypi.tuna.tsinghua.edu.cn/simple`；
- 每次新终端先设 HuggingFace 镜像：`$env:HF_ENDPOINT = "https://hf-mirror.com"`；
- DeepSeek key 只在 `.env`（用户已配），代码里通过 `os.environ["DEEPSEEK_API_KEY"]` 读取。

## 5. 卡住怎么办（升级路径）

1. 先试实施计划里写的预案（如 bge-m3 下载失败 → ModelScope 方案）；
2. 仍失败：**停止**，把完整报错原文 + 你已尝试的步骤贴给用户（用户会转发给验收方拿解法）；
3. 不要反复试同一命令超过 3 次；不要未经允许换方案；
4. 遇到的问题与尝试过的解法，追加到 `STATUS.md` 的「问题与解法」小节。

## 6. 完成报告模板（每个 Task 结束时用）

```
【Task N 完成】
- 创建/修改的文件：……
- 运行命令：……
- 输出（原文）：……
- 与 Expected 的差异：无 / 有（说明）
- 待用户/验收方确认的事项：……
```

## 7. 角色边界一览

| 谁 | 干什么 |
|---|---|
| 用户 | 数据收集（data/faq.txt 条目）、运行、截图、转达报错与验收意见 |
| 你（Cursor） | 按计划写代码、跑测试、commit、报告 |
| 验收方（DSH 助手） | 读 `project1/app/` 代码逐 Task 验收、数据复核、计划维护 |
