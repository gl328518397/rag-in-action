# 读书笔记：上下文工程三件事

Anthropic 把 context engineering 列为 2026 年 AI 工程师的第一技能。核心问题：有限的 context window 里放什么。

三个基本动作：分诊（triage，什么进 prompt 什么不进）、压缩（compaction，长对话怎么压而不丢关键证据）、按需发现（progressive discovery，先看一眼再决定钻多深）。

一个关键数字：Anthropic 工程博客说 agent 任务的 token 消耗约是普通聊天的 4 倍，多代理系统约 15 倍，而 token 用量单独解释了 80% 的效果差异。这句话的经济含义是 token 是可以购买正确性的原料。

Claude Code 的 CLAUDE.md 机制是分诊的工业实现：项目级规则文件在每次会话自动进入 context，相当于开发者提前把"什么最重要"分诊好了。
