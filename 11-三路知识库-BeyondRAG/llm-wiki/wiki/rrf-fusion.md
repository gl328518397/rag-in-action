---
topic: RRF（Reciprocal Rank Fusion）排名融合
type: concept
confidence: medium
source_ids: [05-nashsu-implementation.md]
---
# RRF 融合（Reciprocal Rank Fusion）

把多路检索的排名结果融合为单一排名的方法（背景常识：按各路排名的倒数加权求和，常数 k 用于平滑头部排名的影响）。

## 本库中的实例

[[nashsu-llm-wiki]] 的 [[hybrid-search]] 用 RRF 公式融合关键词和向量两路排名，k 取 60。这是本库目前唯一的 RRF 使用实例，k=60 是该项目的选择，不代表通用推荐值。

来源：[[src-05-nashsu-implementation]]
