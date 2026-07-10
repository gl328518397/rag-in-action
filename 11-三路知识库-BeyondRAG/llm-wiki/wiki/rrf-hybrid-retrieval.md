---
topic: RRF 混合检索——关键词与向量双路排名融合
type: concept
confidence: high
source_ids: [05-nashsu-implementation.md]
---
# RRF 混合检索

关键词检索与向量检索各自产出一路排名，再用 Reciprocal Rank Fusion（RRF）公式把两路融合成单一排序的混合检索做法。

## 已知实例

[[nashsu-llm-wiki]]：关键词和向量两路排名用 RRF 公式融合，k=60。

## 中文场景的配套：三粒度分词

llm_wiki 对中文分词做三粒度处理：全词、单字、双字滑窗同时进索引。原文只描述了该实现的做法，未论证这是中文混合检索的通用必要条件——按反泛化规则不外推。

## 背景补充（confidence: low）

RRF 的一般形式是对每路排名取 1/(k + rank) 后求和，k 用于压平头部排名的差异。此为背景常识，非原文内容。

## 对照

[[agentic-search]] 是不预建索引、现场检索的另一条路线，与"预建索引 + 混合检索"是不同取舍（此对照为本 wiki 推断，原文未直接比较两者）。

来源：[[src-05-nashsu-implementation]]
