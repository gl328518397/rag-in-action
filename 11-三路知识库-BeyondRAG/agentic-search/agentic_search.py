"""Agentic Search 迷你实现 —— 150 行看懂 Claude Code 的检索姿态。

没有 embedding、没有向量库、没有索引。给 LLM 三把成本递增的工具，
让它自己决定怎么搜：

    GLOB  列文件名（近零成本）
    GREP  搜关键词（几百 token）
    READ  读整个文件（几千 token）

LLM 每轮输出一个工具指令，程序执行后把结果喂回去，直到它输出 ANSWER。
这就是一个最小的 agent loop —— 没有框架，纯标准库。

用法：
    python agentic_search.py "Claude Code 为什么放弃向量检索？"
    python agentic_search.py "问题" --corpus /path/to/dir
"""
import fnmatch
import re
import subprocess
import sys
from pathlib import Path

CORPUS = Path(__file__).parent / "corpus"
MAX_TURNS = 8

SYSTEM = """你在一个文档语料库里回答问题。你有三个工具，成本从低到高：

GLOB <pattern>   按文件名模式列文件，如 GLOB *vector*
GREP <keyword>   在所有文件里搜关键词，返回命中行，如 GREP 向量库
READ <filename>  读整个文件，如 READ 02-boris.md

规则：
1. 从便宜的工具开始，有明确线索才 READ（READ 最贵）
2. 每轮只输出一条指令，格式严格是 "工具名 参数"，不要解释
3. 信息足够回答时，输出 "ANSWER" 换行后跟最终回答，回答要标注依据的文件名

问题：{question}

以下是至今的探索记录：
{history}

你的下一条指令："""


def tool_glob(pattern: str) -> str:
    names = [p.name for p in sorted(CORPUS.glob("*")) if fnmatch.fnmatch(p.name, pattern)]
    return "\n".join(names) if names else "（无匹配文件）"


def tool_grep(keyword: str) -> str:
    hits = []
    for p in sorted(CORPUS.glob("*.md")):
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if keyword.lower() in line.lower():
                hits.append(f"{p.name}:{i}: {line.strip()[:90]}")
    return "\n".join(hits[:20]) if hits else "（无命中）"


def tool_read(name: str) -> str:
    p = CORPUS / name.strip()
    if ".." in name or not p.exists():
        return "（文件不存在或路径非法）"
    return p.read_text(encoding="utf-8")


def ask_llm(prompt: str) -> str:
    r = subprocess.run(["claude", "-p"], input=prompt,
                       capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[:300])
    return r.stdout.strip()


def main():
    if len(sys.argv) < 2:
        print('用法: python agentic_search.py "你的问题"')
        sys.exit(1)
    question = sys.argv[1]
    if "--corpus" in sys.argv:
        global CORPUS
        CORPUS = Path(sys.argv[sys.argv.index("--corpus") + 1])

    print(f"[agentic-search] {question}\n")
    history = "（还没开始）"
    spent_reads = 0

    for turn in range(1, MAX_TURNS + 1):
        reply = ask_llm(SYSTEM.format(question=question, history=history))

        if reply.startswith("ANSWER"):
            print(f"\nTurn {turn}: 信息足够，生成回答")
            print("─" * 60)
            print(reply.removeprefix("ANSWER").strip())
            print("─" * 60)
            print(f"\n[stats] 共 {turn} 轮，READ 了 {spent_reads} 个文件")
            return

        m = re.match(r"(GLOB|GREP|READ)\s+(.+)", reply.splitlines()[0])
        if not m:
            history += f"\n[Turn {turn}] 你的输出不是合法指令：{reply[:80]}"
            continue
        tool, arg = m.group(1), m.group(2).strip()
        result = {"GLOB": tool_glob, "GREP": tool_grep, "READ": tool_read}[tool](arg)
        if tool == "READ":
            spent_reads += 1

        shown = result if len(result) < 300 else result[:300] + " ..."
        print(f"Turn {turn}: {tool} {arg}")
        for line in shown.splitlines()[:6]:
            print(f"    {line}")
        history += f"\n[Turn {turn}] {tool} {arg}\n结果:\n{result}\n"

    print("\n[fail] 达到最大轮数还没答出来 —— token 预算保护生效")


if __name__ == "__main__":
    main()
