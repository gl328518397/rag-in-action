"""LLM 调用适配层 —— 默认走 claude CLI（零依赖），可切 OpenAI。

与 11-三路知识库 同款：CLI 子进程零 pip 依赖，换后端只改这一个文件。

用法：
    from llm import ask
    answer = ask("你的 prompt")

切 OpenAI：export LLM_BACKEND=openai OPENAI_API_KEY=sk-...
"""
import json
import os
import subprocess
import urllib.request

BACKEND = os.environ.get("LLM_BACKEND", "claude-cli")
MODEL = os.environ.get("LLM_MODEL", "")  # 空 = 各后端默认


def ask(prompt: str, timeout: int = 300) -> str:
    if BACKEND == "openai":
        return _ask_openai(prompt, timeout)
    return _ask_claude_cli(prompt, timeout)


def _ask_claude_cli(prompt: str, timeout: int) -> str:
    """通过 claude CLI headless 模式调用。"""
    cmd = ["claude", "-p"]
    if MODEL:
        cmd += ["--model", MODEL]
    result = subprocess.run(
        cmd, input=prompt, capture_output=True, text=True, timeout=timeout
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude CLI 失败: {result.stderr[:500]}")
    return result.stdout.strip()


def _ask_openai(prompt: str, timeout: int) -> str:
    """OpenAI 兼容接口（含国产模型的兼容端点）。"""
    api_key = os.environ["OPENAI_API_KEY"]
    base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = MODEL or "gpt-4o-mini"
    req = urllib.request.Request(
        f"{base}/chat/completions",
        data=json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
        }).encode(),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.load(resp)
    return data["choices"][0]["message"]["content"].strip()
