# 读书笔记：向量库选型速记

向量库是 RAG 的存储底座。主流选项：Pinecone（托管 SaaS 先驱）、Milvus/Zilliz（开源大规模）、LanceDB（嵌入式，本地文件即库）、Turbopuffer（对象存储优先的新架构）。

Notion 2026 年 2 月的工程博客记录了从 Pinecone 迁到 Turbopuffer 的收益：容量 10 倍，embedding 基础设施成本降 90% 以上，向量库成本降 60%，端到端查询延迟从 70-100ms 降到 50-70ms。Cursor 也用 Turbopuffer 存代码 embedding。

nashsu 的 llm_wiki 桌面应用选的是 LanceDB 嵌入式模式，schema 极简只有两列（page_id + 定长向量），更新用先删后插模拟 upsert。

有一点值得注意：Claude Code 内置了本地向量索引来加速代码检索，首次打开仓库时会自动对全部源文件做 embedding。
