---
topic: 读书笔记《nashsu/llm_wiki 实现要点》浓缩
type: summary
confidence: high
source_ids: [05-nashsu-implementation.md]
---
# src-05：nashsu/llm_wiki 实现要点

关于 [[nashsu-llm-wiki]] 的实现细节笔记。要点：

- 作者是日本工程师 nashsu，读完 Karpathy 的 gist 后开发的开源桌面应用；技术栈 Tauri v2（Rust）+ React 19 + TypeScript，不是网传的 Python
- 每份文档入库前算 SHA-256 内容指纹，没变就跳过整条 LLM 调用
- ingest 队列并发度硬编码为 1：wiki 页面是共享可变状态，markdown 文件没有锁
- 编译分两步：第一步输出六段固定结构的分析，第二步才生成页面文件
- 提示词头部写明不许输出思考过程，防止推理模型的碎碎念污染 wiki
- 检索为混合式（[[hybrid-search]]）：关键词与向量两路排名用 RRF 融合，k=60（[[rrf-fusion]]）；中文分词三粒度：全词、单字、双字滑窗
- 对已有页面的修改只输出建议不直接改，留人工审核，作为防止错误自动扩散的闸门

相关页面：[[nashsu-llm-wiki]]、[[karpathy-llm-wiki-scheme]]
