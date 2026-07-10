---
topic: agentic search——用工具逐步搜索替代预建向量索引的代码检索方式
type: concept
confidence: high
source_ids: [02-boris-cherny-agentic-search.md, 04-vector-db-notes.md]
---
# Agentic Search

让模型自己拿工具（如 Glob / Grep / Read）逐步搜索代码库的检索方式，替代"预先建向量索引再检索"的 RAG 方案。[[claude-code]] 是从 RAG 切换到这种方式的实例（具体工具阶梯见该页）。

## 对比 RAG 的四个优势（Cherny 陈述）

[[boris-cherny]] 给出 Claude Code 放弃 RAG 的四个理由：

1. **Security**：向量库要独立部署，扩大攻击面
2. **Privacy**：代码要上传给 embedding 服务，企业客户拒绝
3. **Staleness**：代码天天变，索引永远慢半拍
4. **Reliability**：向量检索会静默漏掉东西，且无法审计——agentic search 的每步工具调用则可见

原笔记作者指出：这四个理由全是**运营负担**，不是性能分数。

## 行业跟进（截至 2026 年 5 月）

Windsurf、Cline、Devin、Sourcegraph Amp 都跟进放弃了向量索引。

## 反方证据

[[cursor]] 是唯一坚守向量索引的编程工具，其内部研究称语义检索加 grep 比纯 grep 准确率高 12.5%，大代码库上最明显。因此"agentic search 效果更好"应理解为 Cherny 就 Claude Code 场景的总体判断（且理由集中在运营维度），不能当作性能维度上的一边倒结论，也不应升格为"所有编程工具都应放弃向量索引"。

## 争议记录

一份向量库选型笔记（[[src-04-vector-db-notes]]）称 Claude Code 内置本地向量索引、首次打开仓库自动对全部源文件做 embedding。该说法在笔记中未给出处，与本页有明确出处（Cherny 本人陈述）的结论直接冲突，不采信，本页结论维持不变。

参见：[[karpathy-llm-wiki-scheme]]

来源：[[src-02-boris-cherny-agentic-search]]、[[src-04-vector-db-notes]]
