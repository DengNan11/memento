import json
import os
from datetime import date
from difflib import SequenceMatcher

from config import MEMORY_FILE, MAX_CONTEXT_ENTRIES


def load_memory() -> dict:
    if not os.path.exists(MEMORY_FILE):
        return _empty_memory()
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_memory(memory: dict) -> None:
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    memory["meta"]["last_updated"] = date.today().isoformat()
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)


def get_context_text(memory: dict, limit: int = MAX_CONTEXT_ENTRIES) -> str:
    entries = sorted(memory["entries"], key=lambda e: e["confidence"], reverse=True)
    entries = entries[:limit]
    if not entries:
        return "（暂无关于用户的信息）"
    lines = []
    for e in entries:
        lines.append(f"- [{e['category']}] {e['content']} (置信度: {e['confidence']:.2f})")
    return "\n".join(lines)


def add_entries(memory: dict, new_entries: list[dict]) -> dict:
    today = date.today().isoformat()
    existing = memory["entries"]

    for new_e in new_entries:
        new_e.setdefault("id", _next_id(existing))
        new_e.setdefault("created_at", today)
        new_e.setdefault("last_confirmed", today)
        new_e.setdefault("confidence", _initial_confidence(new_e.get("source", "inferred")))

        similar = _find_similar(new_e["content"], existing)

        if similar:
            if _is_contradiction(new_e["content"], similar["content"]):
                similar["confidence"] = round(similar["confidence"] * 0.7, 3)
                new_e["confidence"] = 0.5
                existing.append(new_e)
            else:
                similar["last_confirmed"] = today
                similar["confidence"] = min(1.0, round(similar["confidence"] + 0.05, 3))
        else:
            existing.append(new_e)

    memory["meta"]["total_conversations"] = memory["meta"].get("total_conversations", 0) + 1
    return memory


def _empty_memory() -> dict:
    return {
        "entries": [],
        "meta": {
            "total_conversations": 0,
            "last_updated": date.today().isoformat(),
        },
    }


def _next_id(entries: list[dict]) -> str:
    max_num = 0
    for e in entries:
        try:
            num = int(e["id"].split("_")[1])
            if num > max_num:
                max_num = num
        except (IndexError, ValueError):
            pass
    return f"e_{max_num + 1:03d}"


def _initial_confidence(source: str) -> float:
    return {
        "user_direct": 0.8,
        "preference": 0.6,
        "inferred": 0.4,
    }.get(source, 0.5)


def _find_similar(content: str, entries: list[dict]) -> dict | None:
    best_match = None
    best_ratio = 0.0
    for e in entries:
        ratio = SequenceMatcher(None, content, e["content"]).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = e
    if best_ratio > 0.6:
        return best_match
    return None


def _is_contradiction(new_content: str, old_content: str) -> bool:
    negation_keywords = ["不", "不是", "不再", "已经不", "换了", "改了", "转"]
    for kw in negation_keywords:
        if kw in new_content and kw not in old_content:
            return True
        if kw in old_content and kw not in new_content:
            return True
    return False
