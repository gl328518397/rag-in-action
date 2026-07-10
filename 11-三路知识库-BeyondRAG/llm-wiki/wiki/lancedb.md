---
topic: LanceDB——嵌入式向量库，本地文件即库
type: entity
confidence: high
source_ids: [04-vector-db-notes.md]
---
# LanceDB

嵌入式向量库，本地文件即库，是 [[vector-database]] 四条选型路线中"嵌入式"路线的代表。

## 采用案例：nashsu 的 llm_wiki

nashsu 的 llm_wiki 桌面应用选用 LanceDB 嵌入式模式。该应用自身的用法（属于这一个应用的选择，非 LanceDB 的通用规范）：

- schema 极简，只有两列：page_id + 定长向量
- 更新用"先删后插"模拟 upsert

注：该应用与 [[karpathy-llm-wiki-scheme]] 同名且形态相近，但两者是否确有渊源，现有 source 未说明，暂不建立同一性关联。

来源：[[src-04-vector-db-notes]]
