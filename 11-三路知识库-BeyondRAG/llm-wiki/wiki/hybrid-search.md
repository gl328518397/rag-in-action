---
topic: 混合检索（关键词 + 向量两路融合）
type: concept
confidence: medium
source_ids: [05-nashsu-implementation.md]
---
# 混合检索（Hybrid Search）

同时跑关键词检索和向量检索两路，再把两路排名融合成一个结果的检索方式。

## 本库中的实例

[[nashsu-llm-wiki]] 的检索是混合式：关键词和向量两路排名用 [[rrf-fusion]] 公式融合（k=60）。该项目还针对中文做了三粒度分词——全词、单字、双字滑窗同时进索引（这是 llm_wiki 一个项目的做法，不构成对混合检索的一般性要求）。

## 与 agentic search 的路线对照

混合检索依赖预建索引（关键词索引 + 向量索引），与 [[agentic-search]] 用工具逐步搜索、不预建向量索引的路线形成对照。llm_wiki 选择了前者。

来源：[[src-05-nashsu-implementation]]
