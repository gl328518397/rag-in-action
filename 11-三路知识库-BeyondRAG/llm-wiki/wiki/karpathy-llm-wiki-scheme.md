---
topic: Karpathy 的 LLM 知识库维护方案（三层结构 + 三操作）
type: concept
confidence: high
source_ids: [01-karpathy-llm-wiki.md, 02-boris-cherny-agentic-search.md, 05-nashsu-implementation.md]
---
# Karpathy LLM Wiki Scheme

[[andrej-karpathy]] 提出的用 LLM 维护个人知识库的方案，以 gist（karpathy/442a6bf555914893e9891c11519de94f）形式发布，几天内获 5000+ star。

## 三层结构

1. **sources/**：存放不可变的原始文档
2. **wiki/**：存放 LLM 写的页面
3. **CLAUDE.md**：写维护规则

## 三个操作

- **ingest**：把新文档编译进 wiki
- **query**：先看目录再取页
- **lint**：全库一致性盘点

## 立论基础

方案的可行性论证依赖于"维护失败是经济问题"这一论断——LLM 把 bookkeeping 成本压到接近零。详见 [[bookkeeping-cost]]。

## 工程实现

该方案已有落地实现：[[nashsu-llm-wiki]]（开源桌面应用），其两步编译、串行 ingest、人工审核闸门等工程细节见该页面。

## 规模边界

Karpathy 自己承认的边界：约 100 份 source、几百个页面是甜蜜区，超出要回到 embedding 基础设施。他的原话是 "works surprisingly well at moderate scale"。

代码检索领域存在平行争论（[[agentic-search]] vs 向量索引），分歧点同样是规模：Cursor 的内部研究称语义检索的准确率优势在大代码库上最明显。两个领域的证据互为呼应，都指向"规模是分水岭"。

来源：[[src-01-karpathy-llm-wiki]]、[[src-05-nashsu-implementation]]
