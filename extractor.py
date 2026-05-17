import json
import re
import requests

from config import MODELS, DEFAULT_MODEL

EXTRACT_PROMPT = """你是一个记忆提取器。回顾以下对话，提取关于用户的重要信息。

规则：
1. 每条信息只包含一个事实，保持原子化
2. category 取值：identity / preference / opinion / project / behavior / relationship / event
3. source 取值：user_direct（用户直接陈述）/ inferred（你推断的）/ preference（用户表达的偏好）
4. 如果没有值得提取的信息，输出空数组 []
5. 只输出 JSON 数组，不要其他内容

输出格式：
[{{"content": "...", "category": "...", "source": "..."}}, ...]

对话内容：
{conversation}
"""


def extract_entries(conversation_text: str, model_key: str = None) -> list[dict]:
    model_key = model_key or DEFAULT_MODEL
    cfg = MODELS[model_key]
    prompt = EXTRACT_PROMPT.format(conversation=conversation_text)

    if cfg["api_type"] == "anthropic":
        content = _call_anthropic(prompt, cfg)
    else:
        content = _call_openai(prompt, cfg)

    if not content:
        return []
    return _parse_entries(content)


def _call_openai(prompt: str, cfg: dict) -> str | None:
    resp = requests.post(
        f"{cfg['base_url']}/chat/completions",
        headers={
            "Authorization": f"Bearer {cfg['api_key']}",
            "Content-Type": "application/json",
        },
        json={
            "model": cfg["model"],
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
        },
        timeout=60,
    )
    data = resp.json()

    if "error" in data:
        print(f"[API 错误: {json.dumps(data['error'], ensure_ascii=False)}]")
        return None

    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        print(f"[API 响应格式异常: {e}]")
        return None


def _call_anthropic(prompt: str, cfg: dict) -> str | None:
    resp = requests.post(
        f"{cfg['base_url']}/v1/messages",
        headers={
            "x-api-key": cfg["api_key"],
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
        json={
            "model": cfg["model"],
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
        },
        timeout=60,
    )
    data = resp.json()

    if "error" in data:
        print(f"[API 错误: {json.dumps(data['error'], ensure_ascii=False)}]")
        return None

    text_parts = []
    for block in data.get("content", []):
        if block.get("type") == "text":
            text_parts.append(block["text"])
    return "\n".join(text_parts) if text_parts else None


def format_conversation(messages: list[dict]) -> str:
    lines = []
    for m in messages:
        if m["role"] == "system":
            continue
        role = "用户" if m["role"] == "user" else "助手"
        lines.append(f"{role}: {m['content']}")
    return "\n".join(lines)


def _parse_entries(text: str) -> list[dict]:
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if not match:
        return []
    try:
        entries = json.loads(match.group())
        if not isinstance(entries, list):
            return []
        valid = []
        for e in entries:
            if isinstance(e, dict) and "content" in e and "category" in e:
                e.setdefault("source", "inferred")
                valid.append(e)
        return valid
    except json.JSONDecodeError:
        return []
