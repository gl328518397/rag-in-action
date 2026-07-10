---
topic: 读书笔记浓缩：Boris Cherny 谈 Claude Code 为什么放弃 RAG
type: summary
confidence: high
source_ids: [02-boris-cherny-agentic-search.md]
---
# Src: Boris Cherny 谈 Claude Code 放弃 RAG

[[boris-cherny]]（[[claude-code]] 技术负责人）在 X 上回复网友时陈述：Claude Code 早期版本用过 RAG 加本地向量库，但很快发现 [[agentic-search]] 总体上效果更好、也更简单。

## 放弃 RAG 的四个理由

全部属于运营负担，而非性能分数（原笔记作者的观察）：

1. **Security**：向量库要独立部署，扩大攻击面
2. **Privacy**：代码要上传给 embedding 服务，企业客户拒绝
3. **Staleness**：代码天天变，索引永远慢半拍
4. **Reliability**：向量检索会静默漏掉东西，且无法审计

## 替代方案

给模型三把成本递增的工具：Glob（列文件名，近零成本）→ Grep（搜关键词，几百 token）→ Read（读整个文件，几千 token）。模型从便宜工具往贵工具走，有明确线索才打开文件。细节见 [[claude-code]]。

## 行业格局（截至 2026 年 5 月）

Windsurf、Cline、Devin、Sourcegraph Amp 都跟进放弃了向量索引。[[cursor]] 是唯一坚守者——其内部研究称语义检索加 grep 比纯 grep 准确率高 12.5%，大代码库上最明显。
