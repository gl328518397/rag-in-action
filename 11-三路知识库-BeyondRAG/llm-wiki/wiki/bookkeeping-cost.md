---
topic: bookkeeping 成本——知识库维护失败的经济学解释
type: concept
confidence: high
source_ids: [01-karpathy-llm-wiki.md, 02-boris-cherny-agentic-search.md, 05-nashsu-implementation.md]
---
# Bookkeeping Cost

[[andrej-karpathy]] 在其 LLM 知识库方案（[[karpathy-llm-wiki-scheme]]）中的核心论断。

## 论断内容

维护知识库最累的不是阅读、不是思考，而是 **bookkeeping（记账式琐事）**，具体包括：

- 交叉引用
- 术语对齐
- 旧断言作废

## 经济学解释

人类维护 wiki 失败是**经济问题**，不是意志力问题。LLM 恰好把这层 bookkeeping 成本压到接近零——原文由此论证 LLM 维护知识库的可行性（此为该方案的立论，非本 wiki 的普遍结论）。

## 代码检索侧的类似现象（编者推断的关联）

[[boris-cherny]] 给出的 Claude Code 放弃 RAG 的 staleness 理由——代码天天变、索引永远慢半拍——可视为同一类现象：维护索引这份 bookkeeping 跟不上源头的变化速度。注意这一关联是本 wiki 的推断，Karpathy 与 Cherny 的原文均未直接建立此联系。

## 实现侧的成本控制手段（编者推断的关联，confidence: medium）

[[nashsu-llm-wiki]] 有两个工程手段可视为压低维护成本、控制维护风险的实例：SHA-256 内容指纹让未变更文档跳过整条 LLM 调用；对已有页面只输出修改建议、留人工审核，原文称其为防止错误自动扩散的闸门。注意：nashsu 原文并未使用 bookkeeping 这一表述，此归类为本 wiki 推断。

参见：[[token-economics]]（成本/收益视角的另一面——token 投入购买正确性；关联为本 wiki 推断）

来源：[[src-01-karpathy-llm-wiki]]、[[src-02-boris-cherny-agentic-search]]、[[src-05-nashsu-implementation]]
