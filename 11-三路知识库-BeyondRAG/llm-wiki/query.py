"""Query（查货）—— index-first 两阶段查询。

阶段 1：只给 LLM 看 index.md（轻量目录），让它决定要拉哪几页
阶段 2：把选中的页面全文给它，生成带出处的回答

对比 RAG：没有 embedding、没有向量库、没有 top-K —— 检索决策由 LLM
看着目录做，而不是由向量相似度做。这正是 per-source compile 的红利：
结构在 ingest 时已经编译好了，query 只需要"看目录取书"。

用法：
    python query.py "Claude Code 为什么放弃 RAG？"
"""
import sys
from pathlib import Path

from llm import ask

ROOT = Path(__file__).parent
WIKI = ROOT / "wiki"
INDEX = ROOT / "index.md"

PICK_PROMPT = """你在查询一个知识库。下面是全部页面的目录。判断回答这个问题需要读哪几页（最多 4 页），只输出文件名，每行一个，不要解释。

问题：{question}

目录：
{index}
"""

ANSWER_PROMPT = """根据下面的 wiki 页面回答问题。要求：
1. 只依据页面内容回答，页面里没有的就说不知道
2. 每个关键论断标注出处页面名，格式 [页面名]
3. 如果页面之间说法冲突，明确指出冲突

问题：{question}

{pages}
"""


def main():
    if len(sys.argv) < 2:
        print('用法: python query.py "你的问题"')
        sys.exit(1)
    question = sys.argv[1]
    index = INDEX.read_text(encoding="utf-8")

    print(f"[query] {question}\n")
    print("阶段 1/2：LLM 看目录选页 ...")
    picked_raw = ask(PICK_PROMPT.format(question=question, index=index))
    picked = [l.strip().lstrip("- ") for l in picked_raw.splitlines() if l.strip().endswith(".md")]
    print(f"  选中 {len(picked)} 页: {', '.join(picked)}")

    pages_text = ""
    for name in picked:
        p = WIKI / name
        if p.exists():
            pages_text += f"\n=== {name} ===\n{p.read_text(encoding='utf-8')}\n"

    print("阶段 2/2：读选中页面生成回答 ...\n")
    answer = ask(ANSWER_PROMPT.format(question=question, pages=pages_text))
    print("─" * 60)
    print(answer)
    print("─" * 60)


if __name__ == "__main__":
    main()
