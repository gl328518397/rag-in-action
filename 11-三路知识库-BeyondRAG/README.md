# 11 · 三路知识库 —— RAG 之外的两条路（加餐）

这门课前十章讲的是 RAG：把文档切片、向量化、检索、生成。这个加餐回答一个课程群里被反复问到的问题：**除了 RAG，2026 年还有哪两条路在跟它竞争，各自什么时候赢？**

三条路的本质区别只有一个——你在什么时候干活、什么时候花钱：

| 路线 | 新资料进来时 | 有人提问时 | 类比 |
|:--|:--|:--|:--|
| RAG（本课 00-10 章） | 切片 + 向量化（便宜） | 检索 + 拼装（便宜） | 中央厨房备菜 |
| Agentic Search | 什么都不做 | LLM 现场翻文件（贵，约 4-15 倍聊天 token） | 现点现买 |
| LLM Wiki | LLM 通读编译（贵，约 35K token/篇） | 读现成百科（便宜） | 先写一本菜谱 |

两个子目录各是一个**能跑的最小实现**，纯 Python 标准库，零 pip 依赖：

- [`llm-wiki/`](llm-wiki/)：Karpathy 2026 年 4 月 LLM Knowledge Base 方案的迷你复刻——ingest（编译入库）/ query（两阶段查询）/ lint（全库盘点）三个操作全实现，含真实运行截图
- [`agentic-search/`](agentic-search/)：Claude Code 检索姿态的迷你复刻——GLOB/GREP/READ 三工具 agent loop，150 行看懂"没有向量库怎么检索"

LLM 调用默认走 `claude` CLI 子进程（装了 Claude Code 就能跑），`export LLM_BACKEND=openai` 可切 OpenAI 兼容端点。

## 建议的打开方式

1. 先跑 `llm-wiki/`：把 5 篇样例笔记编译成 wiki，提问，然后跑 lint——**样例语料里故意埋了一个事实矛盾，看 lint 能不能抓到**
2. 再跑 `agentic-search/`：同样的语料、同样的问题，对比两条路的 token 消耗和回答质量
3. 回头想：你自己场景里的知识，是"稳定沉淀型"（LLM Wiki 甜蜜区）还是"天天在变型"（agentic search 甜蜜区），还是"海量分散型"（RAG 甜蜜区）

两个子目录的 README 里各有一节"好与不好的复盘"——实现和运行过程中真实遇到的坑，不是事后美化的版本。

## 配套书稿

这两条路的选型逻辑（什么时候 RAG 赢、什么时候 Agentic Search 或 LLM Wiki 赢）在配套书稿《现代知识检索系统》里讲透：**第16章「RAG 的未来：边界在消融」**（Long Context、从 RAG 到 Knowledge OS）是这里的原理版，Agentic Search 那半篇也对应**第14章 Agentic RAG**。这个加餐给的是"跑起来是什么样"，书稿给的是"该怎么选"。相邻加餐 [12-双路召回](../12-双路召回-HybridRetrieval/) 讲的是 RAG 之内的另一条路：知识在业务数据库里时怎么建 KB。
