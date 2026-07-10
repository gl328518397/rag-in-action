# 读书笔记：Boris Cherny 谈 Claude Code 为什么放弃 RAG

Boris Cherny 是 Claude Code 的技术负责人。他在 X 上回复网友时说：Claude Code 早期版本用过 RAG 加本地向量库，但很快发现 agentic search 总体上效果更好，而且更简单，没有 RAG 在 security、privacy、staleness、reliability 四个方面的问题。

注意他给的四个理由全是运营负担不是性能分数：向量库要独立部署扩大攻击面；代码要上传给 embedding 服务企业客户拒绝；代码天天变索引永远慢半拍；向量检索会静默漏掉东西且无法审计。

Claude Code 现在的做法是给模型三把成本递增的工具：Glob（列文件名，近零成本）→ Grep（搜关键词，几百 token）→ Read（读整个文件，几千 token）。模型从便宜工具往贵工具走，有明确线索才打开文件。

到 2026 年 5 月，Windsurf、Cline、Devin、Sourcegraph Amp 都跟进放弃了向量索引。Cursor 是唯一坚守者，他们的内部研究说语义检索加 grep 比纯 grep 准确率高 12.5%，大代码库上最明显。
