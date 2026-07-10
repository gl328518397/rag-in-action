---
topic: Claude Code——Anthropic 的编程 agent 及其检索方案演进
type: entity
confidence: high
source_ids: [02-boris-cherny-agentic-search.md, 03-context-engineering.md]
---
# Claude Code

Anthropic 的编程 agent，技术负责人是 [[boris-cherny]]。

## 检索方案演进

早期版本用 RAG 加本地向量库；实测发现 [[agentic-search]] 总体上效果更好、也更简单，遂放弃 RAG。Cherny 给出的四个理由（security / privacy / staleness / reliability）详见 [[agentic-search]]。

## 现行做法：三把成本递增的工具

| 工具 | 作用 | 成本 |
|------|------|------|
| Glob | 列文件名 | 近零 |
| Grep | 搜关键词 | 几百 token |
| Read | 读整个文件 | 几千 token |

模型从便宜工具往贵工具走，有明确线索才打开文件。

## CLAUDE.md：分诊的工业实现

CLAUDE.md 是 Claude Code 的项目级规则文件，每次会话自动进入 context。source 03 将其举为 [[context-engineering]] 中"分诊（triage）"动作的工业实现：开发者提前把"什么最重要"分诊好了。

来源：[[src-02-boris-cherny-agentic-search]]、[[src-03-context-engineering]]
