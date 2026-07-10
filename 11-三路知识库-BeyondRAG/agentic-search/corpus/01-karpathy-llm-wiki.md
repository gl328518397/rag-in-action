# 读书笔记：Karpathy 的 LLM Knowledge Base 设计

2026 年 4 月 2 日 Karpathy 发推介绍他用 LLM 维护个人知识库的方法，两天后放出 gist（karpathy/442a6bf555914893e9891c11519de94f）。几天内 5000+ star。

核心论断：维护知识库最累的不是阅读、不是思考，是 bookkeeping（记账式琐事）——交叉引用、术语对齐、旧断言作废。人类维护 wiki 失败是经济问题不是意志力问题。LLM 恰好把这层成本压到接近零。

方案是三层：sources/ 目录放不可变原始文档，wiki/ 目录放 LLM 写的页面，CLAUDE.md 写维护规则。三个操作：ingest（新文档编译进 wiki）、query（先看目录再取页）、lint（全库一致性盘点）。

Karpathy 自己承认的边界：约 100 份 source、几百个页面是甜蜜区，超出要回到 embedding 基础设施。他的原话是 works surprisingly well at moderate scale。
