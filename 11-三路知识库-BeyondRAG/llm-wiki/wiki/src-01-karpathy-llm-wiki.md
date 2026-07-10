---
topic: 读书笔记《Karpathy 的 LLM Knowledge Base 设计》浓缩
type: summary
confidence: high
source_ids: [01-karpathy-llm-wiki.md]
---
# src-01-karpathy-llm-wiki

单份 source 的浓缩页。原文是一篇读书笔记，记录 [[andrej-karpathy]] 用 LLM 维护个人知识库的方案。

## 要点

- 2026 年 4 月 2 日 Karpathy 发推介绍该方法，两天后放出 gist（karpathy/442a6bf555914893e9891c11519de94f），几天内获 5000+ star。
- 核心论断：维护知识库最累的不是阅读、不是思考，而是 bookkeeping（记账式琐事）——交叉引用、术语对齐、旧断言作废。人类维护 wiki 失败是经济问题不是意志力问题，LLM 恰好把这层成本压到接近零。详见 [[bookkeeping-cost]]。
- 方案结构：三层（sources/ 不可变原始文档、wiki/ LLM 写的页面、CLAUDE.md 维护规则）加三个操作（ingest / query / lint）。详见 [[karpathy-llm-wiki-scheme]]。
- Karpathy 自己承认的规模边界：约 100 份 source、几百个页面是甜蜜区，超出要回到 embedding 基础设施。原话是 "works surprisingly well at moderate scale"。
