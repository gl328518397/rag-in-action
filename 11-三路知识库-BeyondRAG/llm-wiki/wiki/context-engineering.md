---
topic: context engineering——决定有限 context window 里放什么的技能
type: concept
confidence: high
source_ids: [03-context-engineering.md]
---
# Context Engineering（上下文工程）

决定有限的 context window 里放什么的技能。Anthropic 把它列为 2026 年 AI 工程师的第一技能。

## 三个基本动作

原文给出三个基本动作（暂收在本页，不单独立页）：

- **分诊（triage）**：什么进 prompt，什么不进。[[claude-code]] 的 CLAUDE.md 机制是其工业实现——项目级规则文件每次会话自动进入 context，相当于开发者提前把"什么最重要"分诊好了。
- **压缩（compaction）**：长对话怎么压而不丢关键证据。
- **按需发现（progressive discovery）**：先看一眼再决定钻多深。与 [[agentic-search]] 的逐步搜索思路同属"按需检索"一脉（此关联为编者推断，原文未直接建立）。

## 经济视角

为什么值得花 token 做这件事，见 [[token-economics]]。

来源：[[src-03-context-engineering]]
