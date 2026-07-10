"""把终端运行日志渲染成截图风格 PNG。

用法：
    python term_shot.py <log 文件> <输出.png> "窗口标题" [起始行] [行数]

渲染成 mac 风格终端窗口（三个圆点 + 标题栏 + 深色底），宽高比 2.35:1，
可直接嵌入 16:9 幻灯片的图片槽位。
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"

BG = (30, 32, 44)
TITLEBAR = (44, 46, 60)
FG = (220, 223, 228)
GRAY = (130, 135, 150)
ORANGE = (235, 155, 90)
GREEN = (140, 200, 130)
RED = (235, 110, 100)
CYAN = (120, 190, 230)
DOTS = [(255, 95, 86), (255, 189, 46), (39, 201, 63)]


def line_color(line: str):
    s = line.strip()
    if s.startswith(("[skip]", "（", "#")) or s.startswith("─"):
        return GRAY
    if s.startswith(("[ingest]", "[query]", "[lint]", "[agentic-search]", "[done]", "[stats]")):
        return ORANGE
    if "[新建]" in s or "[更新]" in s or "通过" == s:
        return GREEN
    if s.startswith(("[矛盾]", "[孤儿页]", "[断链]", "[guard]", "[fail]")) or "[矛盾]" in s:
        return RED
    if s.startswith(("Step", "阶段", "检查", "Turn")):
        return CYAN
    return FG


def render(log_path: str, out_path: str, title: str, start: int = 0, count: int = 26):
    lines = Path(log_path).read_text(encoding="utf-8").splitlines()[start:start + count]

    W, H = 2820, 1200
    pad, bar_h = 46, 74
    font_size = 34
    line_h = 42

    font = ImageFont.truetype(FONT_PATH, font_size, index=0)
    font_bold = ImageFont.truetype(FONT_PATH, font_size, index=0)

    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # title bar
    d.rectangle([0, 0, W, bar_h], fill=TITLEBAR)
    for i, c in enumerate(DOTS):
        d.ellipse([pad + i * 46, bar_h // 2 - 13, pad + i * 46 + 26, bar_h // 2 + 13], fill=c)
    d.text((W // 2, bar_h // 2), title, font=font, fill=GRAY, anchor="mm")

    # body
    y = bar_h + 28
    for line in lines:
        if y > H - line_h:
            break
        d.text((pad, y), line[:150], font=font, fill=line_color(line))
        y += line_h

    img.save(out_path)
    print(f"saved {out_path} ({len(lines)} lines)")


if __name__ == "__main__":
    args = sys.argv[1:]
    start = int(args[3]) if len(args) > 3 else 0
    count = int(args[4]) if len(args) > 4 else 26
    render(args[0], args[1], args[2], start, count)
