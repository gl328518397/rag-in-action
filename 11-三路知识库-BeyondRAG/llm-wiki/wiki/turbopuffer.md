---
topic: Turbopuffer——对象存储优先架构的向量库
type: entity
confidence: high
source_ids: [04-vector-db-notes.md]
---
# Turbopuffer

对象存储优先架构的新向量库，是 [[vector-database]] 四条选型路线之一的代表。

## Notion 迁移实测数据

Notion 2026 年 2 月的工程博客记录了从 Pinecone 迁移到 Turbopuffer 的收益（以下数据来自 Notion 博客，经 [[src-04-vector-db-notes]] 转述，仅描述 Notion 自身场景）：

- 容量：10 倍
- embedding 基础设施成本：降 90% 以上
- 向量库成本：降 60%
- 端到端查询延迟：从 70-100ms 降到 50-70ms

## 采用者

- **Notion**：从 Pinecone 迁入（见上）
- **[[cursor]]**：用 Turbopuffer 存代码 embedding
