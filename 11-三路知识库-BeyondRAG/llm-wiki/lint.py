"""Lint（盘点）—— 全库一致性检查。

三类检查，故意分成两种实现方式，这个划分本身就是教学点：
- 孤儿页 / 断链：纯图算法，不花一分钱 LLM —— 规则能写清楚的不给 LLM
- 页面矛盾：只有语义检查必须交给 LLM —— 这也是最贵的一步，
  工作量随页面数平方增长（这就是 LLM Wiki 千篇天花板的来源）

用法：
    python lint.py
"""
import re
from pathlib import Path

from llm import ask

ROOT = Path(__file__).parent
WIKI = ROOT / "wiki"

CONTRADICTION_PROMPT = """你是知识库盘点员。逐对检查下面的 wiki 页面，找事实性矛盾（同一件事两个页面说法冲突）。只报告真正的矛盾，措辞差异不算。

输出格式（没有矛盾就输出"未发现矛盾"）：
[矛盾] 页面A vs 页面B
  A 说：...
  B 说：...
  建议：回查原始 source 确认哪个对

{pages}
"""


def load_pages() -> dict:
    return {p.name: p.read_text(encoding="utf-8") for p in sorted(WIKI.glob("*.md"))}


def check_links(pages: dict):
    """纯算法部分：孤儿页 + 断链，零 LLM 成本。"""
    names = {Path(n).stem for n in pages}
    inbound = {n: 0 for n in names}
    broken = []
    for name, text in pages.items():
        for link in re.findall(r"\[\[([^\]]+)\]\]", text):
            stem = link.strip().removesuffix(".md")
            if stem in names:
                inbound[stem] += 1
            else:
                broken.append((name, link))
    orphans = [n for n, c in inbound.items() if c == 0]
    return orphans, broken


def main():
    pages = load_pages()
    print(f"[lint] 盘点 {len(pages)} 个页面\n")

    print("检查 1/3 孤儿页（纯图算法，零 LLM 成本）")
    orphans, broken = check_links(pages)
    for o in orphans:
        print(f"  [孤儿页] {o}.md 没有任何页面链接它")
    if not orphans:
        print("  通过")

    print("\n检查 2/3 断链（纯字符串匹配，零 LLM 成本）")
    for src, link in broken:
        print(f"  [断链] {src} 引用了不存在的 [[{link}]]")
    if not broken:
        print("  通过")

    print("\n检查 3/3 页面矛盾（LLM 交叉比对 —— 最贵的一步，O(n²)）")
    all_pages = "\n".join(f"=== {n} ===\n{t}" for n, t in pages.items())
    report = ask(CONTRADICTION_PROMPT.format(pages=all_pages))
    print("─" * 60)
    print(report)
    print("─" * 60)
    print("\n[done] 盘点完成。矛盾项请回查 sources/ 原文，人工裁决后修 wiki。")


if __name__ == "__main__":
    main()
