---
topic: Cursor——唯一坚持向量索引的编程工具
type: entity
confidence: high
source_ids: [02-boris-cherny-agentic-search.md, 04-vector-db-notes.md]
---
# Cursor

编程工具。截至 2026 年 5 月，在 Windsurf、Cline、Devin、Sourcegraph Amp 均放弃向量索引之后，Cursor 是唯一的坚守者。

## 内部研究

Cursor 的内部研究称：语义检索加 grep 比纯 grep 准确率高 12.5%，在大代码库上最明显。这是 [[agentic-search]] 一边倒叙事的主要反方证据。

## 向量存储实现

Cursor 的代码 embedding 存在 [[turbopuffer]]（对象存储优先架构的向量库）。

来源：[[src-02-boris-cherny-agentic-search]]、[[src-04-vector-db-notes]]
