---
topic: nashsu 的 llm_wiki——Karpathy 方案的桌面应用实现
type: entity
confidence: high
source_ids: [04-vector-db-notes.md, 05-nashsu-implementation.md]
---
# nashsu 的 llm_wiki

日本工程师 [[andrej-karpathy]] gist 的读者 nashsu 开发的开源桌面应用，是 [[karpathy-llm-wiki-scheme]] 的一个具体实现。

## 技术栈

Tauri v2（Rust）+ React 19 + TypeScript。原文特别澄清：网传的 Python 技术栈说法是错的。

## 存储层选型

- 选用 [[lancedb]] 嵌入式模式，本地文件即库，无需独立服务
- schema 极简，只有两列：page_id + 定长向量
- 更新操作用先删后插模拟 upsert（LanceDB 该 schema 下不走原生 upsert）

这一实践表明极简两列 schema 足以支撑桌面级 wiki 应用的向量检索。

## Ingest 工程细节

- **内容指纹去重**：每份文档入库前算 SHA-256，内容未变则跳过整条 LLM 调用（成本控制手段）
- **串行队列**：ingest 并发度硬编码为 1——wiki 页面是共享可变状态，markdown 文件没有锁
- **两步编译**：第一步输出六段固定结构的分析，第二步才生成页面文件
- **抑制思考输出**：提示词头部写明不许输出思考过程，防止推理模型的碎碎念污染 wiki

## 检索

采用 [[hybrid-search]]：关键词和向量两路排名用 [[rrf-fusion]] 融合（k=60）。中文分词做三粒度处理：全词、单字、双字滑窗同时进索引。

## 人工审核闸门

对已有页面的修改只输出建议、不直接改，保留人工审核环节——这是防止错误自动扩散的闸门。

来源：[[src-04-vector-db-notes]]、[[src-05-nashsu-implementation]]
