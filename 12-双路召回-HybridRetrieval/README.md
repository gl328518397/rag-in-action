# 12 · 双路召回 —— SQL + Vector，MySQL 里的历史数据该怎么建 KB（加餐）

这个加餐来自课程群里的一个真实提问：

> 我在做一个测试平台，要根据用户需求从 KB 里召回历史数据、用 AI 生成测试用例。历史数据都存在 MySQL 里——用例名、描述、对应的脚本。那这个 KB 是直接查 MySQL，还是把数据整理一下放进向量数据库？怎么建召回效果会更好？

这个问题的价值在于它是一大类场景的代表：**你的知识不在文档里，而在业务数据库里**。历史工单、客服记录、测试用例、审批单——都是"结构化字段 + 自由文本"的混合体。答案不是二选一：

| 数据形态 | 走哪路 | 原因 |
|:--|:--|:--|
| 纯结构化字段（模块、优先级、参数、状态） | SQL 路 | 压成向量反而损耗质量——`priority='P0'` 这种精确约束，向量做不了 |
| 自由文本（用例名、描述、脚本） | Vector 路 | "重复回调只入账一次"和"重复发起退款"字段上无关，语义上同族 |
| 两者混合（本场景） | **双路召回 + 去重融合** | 各吃各的召回面，融合处标注来源，互补性可审计 |

本目录是这个方案的**能跑的最小实现**，纯 Python 标准库，零 pip 依赖：

- `setup_db.py` —— 用 SQLite 模拟 MySQL，建 15 条历史用例（换真 MySQL 只改连接层）
- `hybrid_retrieval.py` —— SQL 路（LLM 生成 SELECT）+ Vector 路（TF-IDF 余弦，embedding 的零依赖替身）→ RRF 融合去重 → 生成新用例
- `llm.py` —— 与 11 讲同款的 LLM 适配层，默认 claude CLI，可切 OpenAI

## 跑起来

```bash
python3 setup_db.py
python3 hybrid_retrieval.py "订单取消后重复发起退款，应只退一次"
python3 hybrid_retrieval.py "需求" --retrieve-only   # 只看召回，不生成
```

## 真实运行记录一：双路互补

```
需求：订单取消后重复发起退款，应只退一次

━━ SQL 路（LLM 生成查询，吃结构化字段）
  SELECT id, module, name FROM test_cases WHERE module IN ('订单', '支付')
    AND (name LIKE '%退款%' OR description LIKE '%退款%'
    OR name LIKE '%取消%' OR description LIKE '%重复%') LIMIT 4;
  命中 #5 【订单】取消订单后库存回滚
  命中 #6 【订单】退款申请审核通过后原路退回
  命中 #8 【支付】支付回调幂等性校验

━━ Vector 路（TF-IDF 余弦，embedding 的零依赖替身）
  命中 #6 【订单】退款申请审核通过后原路退回  (0.295)
  命中 #5 【订单】取消订单后库存回滚  (0.243)
  命中 #8 【支付】支付回调幂等性校验  (0.199)
  命中 #7 【订单】订单超时未支付自动关闭  (0.049)

━━ 融合去重（RRF）
  #5 【订单】取消订单后库存回滚  [SQL+Vector]
  #6 【订单】退款申请审核通过后原路退回  [SQL+Vector]
  #8 【支付】支付回调幂等性校验  [SQL+Vector]
  #7 【订单】订单超时未支付自动关闭  [Vector]
```

注意 #8：需求里没有"幂等"两个字，但**跨模块的支付幂等用例被两路都召回了**——它正是生成"只退一次"这条新用例最需要参考的历史资产。生成结果（完整输出见 `run_full.txt`）：

```python
def test_duplicate_refund_after_cancel_refunds_once():
    order = create_paid_order("alice")
    cancel_order(order.id)
    req1 = apply_refund(order.id)
    req2 = apply_refund(order.id)  # 同一订单重复发起退款
    approve_refund(req1.id)
    assert order.reload().status == "REFUNDED"
    assert refund_entries(order.id) == 1
```

断言写到了"退款流水只有一条"——这个测法直接来自 #8 幂等用例的 `ledger_entries(order.id) == 1`。召回质量直接决定生成质量，这就是这条链路上 RAG 的全部意义。

## 真实运行记录二：SQL 路的真实翻车

```
需求：参考支付模块 P0 级别的用例，生成一条大额支付需要短信验证的用例

━━ SQL 路（LLM 生成查询，吃结构化字段）
  SELECT id, module, name FROM test_cases
  WHERE module = '支付' AND priority = 'P0'
    AND (name LIKE '%大额%' OR ... OR description LIKE '%验证%')
  （无命中）

━━ Vector 路（TF-IDF 余弦，embedding 的零依赖替身）
  命中 #3 【登录】验证码过期后登录失败  (0.222)
  命中 #10 【支付】支付超时后订单状态回滚  (0.095)
  ...
```

SQL 路把模糊关键词 **AND** 进了精确约束——`module='支付' AND priority='P0'` 单独查明明有幂等校验那条 P0 用例，加上 `LIKE '%大额%'` 之后清零了。Vector 路这时候兜住了底：捞回了语义相近的验证码用例。这次翻车没有修饰，原样放在这里（`run_structured.txt`），因为它正是双路架构存在的理由之一：**任何一路都会以你想不到的方式漏召回，另一路是它的保险**。

## 复盘：好与不好

**好的部分：**

1. **来源标注让互补性可审计**。每条融合结果带 `[SQL+Vector]` / `[Vector]` 标签，哪路贡献了哪条一目了然——排查"为什么没召回到 X"时，能定位到具体哪一路的问题。
2. **RRF 融合不需要调分数**。两路的分数量纲完全不同（SQL 没有分数，TF-IDF 是余弦值），倒数排名融合只看排名不看分数，一行公式解决合并问题——这也是 Milvus/Elasticsearch 混合检索的默认做法。
3. **结构化字段留在 SQL 里，文本才进向量**。15 条用例换成 15 万条，SQL 路的精确过滤成本几乎不变——这是"全部压向量"方案做不到的。

**不好的部分：**

1. **LLM 生成的 SQL 会过度约束**（运行记录二）。生产上要么让 LLM 生成"约束递减"的多条查询（先全条件、空了再放宽），要么把精确约束和关键词拆开——`module/priority` 做硬过滤，`LIKE` 只加分不做 AND 条件。
2. **TF-IDF 只是 embedding 的替身**。字符 bigram 能抓住"重复退款"↔"重复回调"这种字面重叠，抓不住"幂等"↔"只退一次"这种纯语义关联。生产上换真 embedding 模型（课程 03 章），这里为零依赖妥协。
3. **SQL 路生成有延迟和不确定性**。每次查询多一次 LLM 调用，同一需求两次生成的 SQL 可能不同。高频场景可以把"需求模式 → SQL 模板"缓存下来，LLM 只填参数。

## 生产化清单

把这个迷你实现搬进真实测试平台时，各组件的升级路径：

| Demo 组件 | 生产替换 |
|:--|:--|
| SQLite | MySQL 本尊，表结构不变 |
| TF-IDF 余弦 | embedding 模型 + 向量库（模块/函数名/参数进 metadata，支持过滤） |
| `sql_search()` 函数 | 包装成 MCP 工具挂给大模型——SQL 路在生产里的标准形态 |
| 每次全量建索引 | 向量库增量写入，MySQL binlog 或定时同步触发 |
| RRF 融合 | 保留即可，或换向量库自带的 hybrid search |

三条路的选型逻辑（RAG / Agentic Search / LLM Wiki）见 [11-三路知识库](../11-三路知识库-BeyondRAG/)；本加餐是其中 RAG 这条路在"业务数据库场景"下的具体形态。
