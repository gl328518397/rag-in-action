"""双路召回迷你实现 —— SQL 路 + Vector 路，去重融合，生成新测试用例。

回答课程群里一个真实提问：测试平台的历史用例存在 MySQL 里
（用例名、描述、脚本），KB 该直接查 MySQL，还是压进向量库？

答案是两路都要，各干各的活：

    SQL 路     LLM 根据需求生成 SELECT 查询，吃结构化字段的精确约束
               （模块、优先级）—— 结构化数据压成向量反而损耗质量
    Vector 路  用例名 + 描述做语义相似召回，吃跨模块的"意思相近"
               —— "重复回调只入账一次"和"重复提交订单"字段上无关，语义上同族

    融合       RRF（倒数排名融合）合并两路排名 + 按 id 去重，
               每条命中标注来自哪一路，互补性一眼可见

Vector 路用纯标准库 TF-IDF（字符 bigram 分词 + 余弦相似度）当 embedding
的零依赖替身——生产上换成真 embedding 模型 + 向量库，接口形态不变。

用法：
    python3 setup_db.py                      # 先建库
    python3 hybrid_retrieval.py "订单取消后重复发起退款，应只退一次"
    python3 hybrid_retrieval.py "需求" --retrieve-only   # 只看召回，不生成
"""
import math
import re
import sqlite3
import sys
from collections import Counter
from pathlib import Path

from llm import ask

DB_PATH = Path(__file__).parent / "testcases.db"
TOP_K = 4        # 每路取前 K
RRF_K = 60       # RRF 平滑常数，业界惯用 60


# ---------------- Vector 路：纯标准库 TF-IDF ----------------

def tokenize(text: str) -> list:
    """英文按词、中文按字符 bigram 切分——零依赖场景的够用分词。"""
    tokens = re.findall(r"[a-z0-9_]+", text.lower())
    for run in re.findall(r"[一-鿿]+", text):
        if len(run) == 1:
            tokens.append(run)
        else:
            tokens += [run[i:i + 2] for i in range(len(run) - 1)]
    return tokens


def build_index(rows: list) -> dict:
    """对 用例名+描述 建 TF-IDF 索引。id → 稀疏向量。"""
    docs = {r["id"]: tokenize(r["name"] + " " + r["description"]) for r in rows}
    df = Counter(t for toks in docs.values() for t in set(toks))
    n = len(docs)
    idf = {t: math.log(n / (1 + c)) + 1 for t, c in df.items()}
    vecs = {}
    for doc_id, toks in docs.items():
        tf = Counter(toks)
        vecs[doc_id] = {t: c * idf[t] for t, c in tf.items()}
    return {"vecs": vecs, "idf": idf}


def cosine(a: dict, b: dict) -> float:
    dot = sum(v * b.get(t, 0.0) for t, v in a.items())
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    return dot / (na * nb) if na and nb else 0.0


def vector_search(query: str, index: dict, k: int = TOP_K) -> list:
    """返回 [(id, score)]，按相似度降序。"""
    tf = Counter(tokenize(query))
    qvec = {t: c * index["idf"].get(t, 0.0) for t, c in tf.items()}
    scored = [(doc_id, cosine(qvec, vec)) for doc_id, vec in index["vecs"].items()]
    scored = [(i, s) for i, s in scored if s > 0]
    return sorted(scored, key=lambda x: -x[1])[:k]


# ---------------- SQL 路：LLM 生成查询 ----------------

SQL_PROMPT = """你是测试平台的查询助手。历史用例表结构如下：

CREATE TABLE test_cases (
    id INTEGER PRIMARY KEY,
    module TEXT,       -- 取值：登录/订单/支付/用户/库存
    priority TEXT,     -- 取值：P0/P1/P2
    name TEXT,         -- 用例名
    description TEXT   -- 用例描述
);

用户需求：{requirement}

生成一条 SQLite SELECT 语句，找出与该需求最相关的历史用例。要求：
1. 只输出 SQL 本身，不要解释、不要代码块标记
2. 用 module 精确约束 + name/description 的 LIKE 模糊约束组合
3. SELECT id, module, name 即可，LIMIT {k}
{feedback}"""


def sql_search(requirement: str, conn, k: int = TOP_K) -> tuple:
    """LLM 生成 SELECT → 执行。失败带错误信息重试一次。返回 (sql, [id])。"""
    feedback = ""
    for _ in range(2):
        sql = ask(SQL_PROMPT.format(requirement=requirement, k=k,
                                    feedback=feedback)).strip()
        sql = re.sub(r"^```\w*|```$", "", sql, flags=re.M).strip()
        if not sql.lower().startswith("select"):
            feedback = f"\n上次输出不是 SELECT 语句，重新生成：{sql[:100]}"
            continue
        try:
            ids = [r[0] for r in conn.execute(sql).fetchall()]
            return sql, ids
        except sqlite3.Error as e:
            feedback = f"\n上次生成的 SQL 执行报错（{e}），修正后重新生成：{sql}"
    return sql, []


# ---------------- 融合去重：RRF ----------------

def rrf_merge(sql_ids: list, vec_ids: list, k: int = TOP_K) -> list:
    """倒数排名融合：score = Σ 1/(RRF_K + rank)。返回 [(id, score, 来源)]。"""
    scores, sources = Counter(), {}
    for rank, doc_id in enumerate(sql_ids):
        scores[doc_id] += 1 / (RRF_K + rank + 1)
        sources.setdefault(doc_id, set()).add("SQL")
    for rank, (doc_id, _) in enumerate(vec_ids):
        scores[doc_id] += 1 / (RRF_K + rank + 1)
        sources.setdefault(doc_id, set()).add("Vector")
    merged = [(doc_id, s, "+".join(sorted(sources[doc_id])))
              for doc_id, s in scores.most_common(k)]
    return merged


# ---------------- 生成新用例 ----------------

GEN_PROMPT = """你是资深测试工程师。参考以下历史用例的写法和风格，
为新需求生成一条测试用例。

新需求：{requirement}

历史用例（双路召回的结果）：
{cases}

输出格式（不要代码块标记外的多余解释）：
用例名：...
模块：...
优先级：...
描述：...
脚本：
```python
...
```"""


def generate_case(requirement: str, cases: list) -> str:
    blocks = []
    for c in cases:
        blocks.append(f"【{c['module']}/{c['priority']}】{c['name']}\n"
                      f"描述：{c['description']}\n脚本：\n{c['script']}")
    return ask(GEN_PROMPT.format(requirement=requirement,
                                 cases="\n\n".join(blocks)))


# ---------------- 主流程 ----------------

def main():
    if len(sys.argv) < 2:
        print('用法: python3 hybrid_retrieval.py "你的测试需求" [--retrieve-only]')
        sys.exit(1)
    requirement = sys.argv[1]
    if not DB_PATH.exists():
        print("先运行 python3 setup_db.py 建库")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute("SELECT * FROM test_cases")]
    by_id = {r["id"]: r for r in rows}
    index = build_index(rows)

    print(f"需求：{requirement}\n")

    print("━━ SQL 路（LLM 生成查询，吃结构化字段）")
    sql, sql_ids = sql_search(requirement, conn)
    print(f"  {sql}")
    for i in sql_ids:
        print(f"  命中 #{i} 【{by_id[i]['module']}】{by_id[i]['name']}")
    if not sql_ids:
        print("  （无命中）")

    print("\n━━ Vector 路（TF-IDF 余弦，embedding 的零依赖替身）")
    vec_hits = vector_search(requirement, index)
    for i, score in vec_hits:
        print(f"  命中 #{i} 【{by_id[i]['module']}】{by_id[i]['name']}  ({score:.3f})")
    if not vec_hits:
        print("  （无命中）")

    print("\n━━ 融合去重（RRF）")
    merged = rrf_merge(sql_ids, vec_hits)
    for doc_id, score, src in merged:
        print(f"  #{doc_id} 【{by_id[doc_id]['module']}】"
              f"{by_id[doc_id]['name']}  [{src}]")

    if "--retrieve-only" in sys.argv:
        return

    print("\n━━ 生成的新用例")
    cases = [by_id[doc_id] for doc_id, _, _ in merged]
    print(generate_case(requirement, cases))


if __name__ == "__main__":
    main()
