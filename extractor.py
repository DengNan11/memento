import json
import re

from config import BASE_URL, API_KEY, MODEL

EXTRACT_PROMPT = """你是一个记忆提取器。回顾以下对话，提取关于用户的重要信息。

规则：
1. 每条信息只包含一个事实，保持原子化
2. category 取值：identity / preference / opinion / project / behavior / relationship / event
3. source 取值：user_direct（用户直接陈述）/ inferred（你推断的）/ preference（用户表达的偏好）
4. 如果没有值得提取的信息，输出空数组 []
5. 只输出 JSON 数组，不要其他内容

输出格式：
[
  {"content": "...", "category": "...", "source": "..."},
  ...
]

对话内容：
{conversation}
"""


def extract_entries(conversation_text: str) -> list[dict]:
    import requests

    prompt = EXTRACT_PROMPT.format(conversation=conversation_text)

    resp = requests.post(
        f"{BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
        },
        timeout=60,
    )
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]
    return _parse_entries(content)


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
