"""Ingest（进货）—— 把 sources/ 里的原始文档编译成 wiki/ 页面。

实现了 Karpathy LLM Wiki 方案的核心操作，三个工程细节照搬 nashsu/llm_wiki：
1. 两步编译链：Step1 分析（六段固定结构）→ Step2 生成（FILE block）
2. SHA-256 内容指纹去重：文档没变就跳过整条 LLM 调用
3. 反思考污染：prompt 头部禁止输出 chain-of-thought

用法：
    python ingest.py            # 编译 sources/ 下所有新文档
    python ingest.py --force    # 忽略指纹缓存全量重编
"""
import hashlib
import json
import re
import sys
from pathlib import Path

from llm import ask

ROOT = Path(__file__).parent
SOURCES = ROOT / "sources"
WIKI = ROOT / "wiki"
INDEX = ROOT / "index.md"
CACHE = ROOT / ".ingest-cache.json"
SCHEMA = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")

NO_COT = (
    "Do not output chain-of-thought, hidden reasoning, or a thinking "
    "transcript. Reason internally and write only the final output.\n\n"
)

ANALYSIS_PROMPT = NO_COT + """你是知识库编译器的分析阶段。阅读下面的新文档，对照现有 wiki 目录，输出恰好六段固定结构的分析（标题必须一字不差）：

## Key Entities
[本文提到的具体事物（产品/人/公司/工具），每行一个，附一句话说明]

## Key Concepts
[本文讨论的抽象概念，每行一个，附一句话说明]

## Main Arguments
[本文承重的论断和证据，每行一条]

## Connections to Existing Wiki
[跟现有 wiki 页面的关联，引用页面文件名，说明关联理由；没有就写"无"]

## Contradictions
[本文的说法跟现有 wiki 有没有冲突之处，具体指出；没有就写"无"]

## Recommendations
[建议新建哪些页面（文件名用英文小写连字符）、更新哪些现有页面]

=== 现有 wiki 目录 ===
{index}

=== 新文档（{name}）===
{content}
"""

GENERATION_PROMPT = NO_COT + """你是知识库编译器的生成阶段。根据下面的分析结果，生成 wiki 页面。

规则（来自 CLAUDE.md schema）：
{schema_rules}

两条反污染硬规则：
1. 保持主语边界：断言是关于 A 的，不许写到 B 的页面里
2. 禁止泛化：单个产品的做法不许升格成"这类产品都应该"

输出格式：每个页面一个 FILE block，格式如下（路径只允许 wiki/ 下的相对路径）：

FILE: wiki/xxx.md
---
topic: 页面主题
type: entity | concept | summary
confidence: high | medium | low
source_ids: [{name}]
---
（页面正文，markdown，可用 [[其他页面名]] 交叉引用）
ENDFILE

=== 分析结果 ===
{analysis}

=== 原文（供引用核对）===
{content}
"""


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def load_cache() -> dict:
    return json.loads(CACHE.read_text()) if CACHE.exists() else {}


def build_index() -> str:
    lines = []
    for page in sorted(WIKI.glob("*.md")):
        first = page.read_text(encoding="utf-8").split("\n")
        topic = next((l.split(":", 1)[1].strip() for l in first if l.startswith("topic:")), page.stem)
        lines.append(f"- {page.name}: {topic}")
    return "\n".join(lines) if lines else "（wiki 还是空的）"


def parse_file_blocks(text: str):
    """解析 FILE block。路径逃逸防护照搬 nashsu：拒绝 .. 和绝对路径。"""
    pattern = re.compile(r"FILE:\s*(\S+)\n(.*?)ENDFILE", re.DOTALL)
    for m in pattern.finditer(text):
        path, body = m.group(1).strip(), m.group(2).strip()
        if ".." in path or path.startswith("/") or not path.startswith("wiki/"):
            print(f"  [guard] 拒绝可疑路径: {path}")
            continue
        yield path, body


def ingest_one(doc: Path, index: str) -> int:
    content = doc.read_text(encoding="utf-8")
    print(f"\n[ingest] {doc.name} ({len(content)} chars)")

    print("  Step 1/2 分析中 ...")
    analysis = ask(ANALYSIS_PROMPT.format(index=index, name=doc.name, content=content))
    six = len(re.findall(r"^## ", analysis, re.MULTILINE))
    print(f"  分析完成：{six} 段结构")

    print("  Step 2/2 生成 wiki 页面 ...")
    generated = ask(GENERATION_PROMPT.format(
        schema_rules=SCHEMA, analysis=analysis, name=doc.name, content=content))

    n = 0
    for path, body in parse_file_blocks(generated):
        target = ROOT / path
        exists = "更新" if target.exists() else "新建"
        target.write_text(body + "\n", encoding="utf-8")
        print(f"  [{exists}] {path}")
        n += 1
    return n


def main():
    force = "--force" in sys.argv
    cache = {} if force else load_cache()
    total = 0

    for doc in sorted(SOURCES.glob("*.md")):
        fp = sha256(doc.read_text(encoding="utf-8"))
        if cache.get(doc.name) == fp:
            print(f"[skip] {doc.name} 内容指纹未变，跳过（省一次 LLM 调用）")
            continue
        total += ingest_one(doc, build_index())
        cache[doc.name] = fp
        CACHE.write_text(json.dumps(cache, indent=2))

    INDEX.write_text("# Wiki 目录\n\n" + build_index() + "\n", encoding="utf-8")
    print(f"\n[done] 本次写入 {total} 个页面，目录已更新 → index.md")


if __name__ == "__main__":
    main()
