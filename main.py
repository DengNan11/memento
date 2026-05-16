import sys

from config import API_KEY, BASE_URL, MODEL, EXTRACT_BATCH_SIZE
from memory import load_memory, save_memory, get_context_text, add_entries
from extractor import extract_entries, format_conversation

import requests


def call_llm(messages: list[dict]) -> str:
    resp = requests.post(
        f"{BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL,
            "messages": messages,
            "temperature": 0.7,
        },
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def build_system_prompt(memory: dict) -> str:
    context = get_context_text(memory)
    return f"""你是一个个人助手。以下是你对用户的了解：

{context}

请基于这些了解来辅助用户。不要主动暴露你知道这些信息，除非自然地需要引用。
回复简洁、自然，像一个了解用户的朋友。"""


def do_extract(messages: list[dict], memory: dict) -> None:
    conv_text = format_conversation(messages)
    if not conv_text.strip():
        return
    print("\n[记忆提取中...]")
    try:
        entries = extract_entries(conv_text)
        if entries:
            memory = add_entries(memory, entries)
            save_memory(memory)
            print(f"[提取到 {len(entries)} 条新记忆]")
            for e in entries:
                print(f"  + [{e['category']}] {e['content']}")
        else:
            print("[本轮未提取到新记忆]")
    except Exception as e:
        import traceback
        print(f"[提取失败: {e}]")
        traceback.print_exc()


def main():
    if not API_KEY:
        print("错误：未设置 DEEPSEEK_API_KEY，请在 .env 文件中配置。")
        sys.exit(1)

    memory = load_memory()
    system_prompt = build_system_prompt(memory)
    messages = [{"role": "system", "content": system_prompt}]

    entry_count = len(memory["entries"])
    conv_count = memory["meta"].get("total_conversations", 0)
    print(f"=== Memento 个人记忆助手 ===")
    print(f"已有记忆: {entry_count} 条 | 历史对话: {conv_count} 轮")
    print(f"输入 /quit 退出 | /memory 查看记忆 | /clear 清空记忆")
    print()

    turn_count = 0

    while True:
        try:
            user_input = input("你: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not user_input:
            continue

        if user_input == "/quit":
            do_extract(messages, memory)
            print("再见！记忆已保存。")
            break

        if user_input == "/memory":
            print(f"\n当前记忆 ({len(memory['entries'])} 条):")
            print(get_context_text(memory))
            print()
            continue

        if user_input == "/clear":
            memory = {"entries": [], "meta": {"total_conversations": 0, "last_updated": ""}}
            save_memory(memory)
            messages = [{"role": "system", "content": build_system_prompt(memory)}]
            print("[记忆已清空]\n")
            continue

        messages.append({"role": "user", "content": user_input})

        try:
            response = call_llm(messages)
        except Exception as e:
            print(f"[调用失败: {e}]\n")
            messages.pop()
            continue

        messages.append({"role": "assistant", "content": response})
        print(f"助手: {response}\n")

        turn_count += 1
        if turn_count % EXTRACT_BATCH_SIZE == 0:
            do_extract(messages, memory)
            messages = [{"role": "system", "content": build_system_prompt(memory)}]


if __name__ == "__main__":
    main()
