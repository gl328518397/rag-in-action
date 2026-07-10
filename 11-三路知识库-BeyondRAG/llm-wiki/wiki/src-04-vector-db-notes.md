---
topic: source 04 浓缩——向量库选型速记
type: summary
confidence: high
source_ids: [04-vector-db-notes.md]
---
# Src: 04-vector-db-notes

一份向量库选型读书笔记的浓缩。

## 核心内容

- 向量库是 RAG 的存储底座，主流选项四条路线：Pinecone（托管 SaaS 先驱）、Milvus/Zilliz（开源大规模）、LanceDB（嵌入式，本地文件即库）、Turbopuffer（对象存储优先的新架构）。全景见 [[vector-database]]。
- 引 Notion 2026 年 2 月工程博客的迁移数据（Pinecone → Turbopuffer）：容量 10 倍、embedding 基础设施成本降 90% 以上、向量库成本降 60%、端到端查询延迟从 70-100ms 降到 50-70ms。详见 [[turbopuffer]]。
- [[cursor]] 也用 Turbopuffer 存代码 embedding。
- nashsu 的 llm_wiki 桌面应用选 [[lancedb]] 嵌入式模式：schema 两列（page_id + 定长向量），更新用先删后插模拟 upsert。

## 争议断言（不采信，仅存档）

原文称："Claude Code 内置了本地向量索引来加速代码检索，首次打开仓库时会自动对全部源文件做 embedding。"

该断言在原文中未给任何出处，且与 [[src-02-boris-cherny-agentic-search]]（Cherny 本人陈述 Claude Code 放弃向量索引、改用 [[agentic-search]]）直接冲突。按 schema 硬规则 1、2，此断言不写入 [[claude-code]] 页面，仅在本页如实记录原文说法并标注冲突。
