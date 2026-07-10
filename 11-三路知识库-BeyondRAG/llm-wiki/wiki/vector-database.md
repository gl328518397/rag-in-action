---
topic: 向量库——RAG 存储底座的选型全景
type: concept
confidence: high
source_ids: [04-vector-db-notes.md]
---
# Vector Database

向量库是 RAG 的存储底座。据选型笔记（[[src-04-vector-db-notes]]），主流选项分四条路线：

| 路线 | 代表产品 | 定位 |
|---|---|---|
| 托管 SaaS | Pinecone | 该路线的先驱 |
| 开源大规模 | Milvus / Zilliz | Zilliz 为 Milvus 的商业化公司 |
| 嵌入式 | [[lancedb]] | 本地文件即库 |
| 对象存储优先 | [[turbopuffer]] | 新架构 |

Pinecone 和 Milvus 目前只有一句话定位，信息量不足以单独立页，先收在本页；后续 source 充实后再拆。

## 与 agentic search 的对照

"预建向量索引再检索"是与 [[agentic-search]]（模型拿工具逐步搜索、不预建索引）相对照的另一条代码检索路线。两条路线在编程工具领域的取舍见 [[agentic-search]] 与 [[cursor]]。
