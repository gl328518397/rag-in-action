# Wiki Schema（编译器规格说明书）

这份文件教 LLM 怎么维护本知识库。Karpathy 方案的第三层——schema 决定 wiki 长成知识还是长成垃圾。

## 页面类型

- **entity**：具体事物（产品 / 人 / 公司 / 工具）单独立页，如 claude-code.md
- **concept**：跨文档的抽象概念立页，如 agentic-search.md
- **summary**：单份 source 的浓缩页，文件名 src-<源文件名>.md

## 命名

文件名一律英文小写连字符，如 `vector-database.md`。中文主题用英文译名。

## Frontmatter 必填四字段

topic / type / confidence / source_ids。confidence 按证据强度自评：
原文直接说的 = high；从原文合理推断的 = medium；背景常识补充的 = low。

## 硬规则

1. 断言必须能回溯到 source_ids 里的原文——写不出出处的不要写
2. 不确定的措辞保留不确定性，禁止把"可能"改写成"是"
3. 两个页面讲同一个东西时合并，但**合并前必须确认它们真是同一个东西**
4. 交叉引用用 [[页面名]]，引用前确认目标页面存在或本次会创建
