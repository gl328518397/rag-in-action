---
topic: source 03（读书笔记：上下文工程三件事）的浓缩页
type: summary
confidence: high
source_ids: [03-context-engineering.md]
---
# Source 03：读书笔记——上下文工程三件事

一篇读书笔记，核心问题：有限的 context window 里放什么。

## 要点

1. Anthropic 把 [[context-engineering]] 列为 2026 年 AI 工程师的第一技能。
2. 上下文工程有三个基本动作：分诊（triage）、压缩（compaction）、按需发现（progressive discovery）——详见 [[context-engineering]]。
3. 笔记转述 Anthropic 工程博客的一组数字：agent 任务 token 消耗约为普通聊天 4 倍，多代理系统约 15 倍，token 用量单独解释了 80% 的效果差异；笔记作者由此提出"token 是可以购买正确性的原料"的经济含义——详见 [[token-economics]]。注意这些数字是二手转述，非博客原文。
4. [[claude-code]] 的 CLAUDE.md 机制被笔记举为分诊的工业实现：项目级规则文件每次会话自动进入 context，相当于开发者提前把"什么最重要"分诊好了。
