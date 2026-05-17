import os
import webbrowser
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import API_KEY, BASE_URL, MODEL, EXTRACT_BATCH_SIZE
from memory import load_memory, save_memory, get_context_text, add_entries
from extractor import extract_entries, format_conversation

import requests


# 全局对话状态
class Session:
    def __init__(self):
        self.messages: list[dict] = []
        self.turn_count: int = 0
        self.memory: dict = {}

    def reset(self):
        self.messages = [{"role": "system", "content": build_system_prompt(self.memory)}]
        self.turn_count = 0


session = Session()


def build_system_prompt(memory: dict) -> str:
    context = get_context_text(memory)
    return f"""你是一个个人助手。以下是你对用户的了解：

{context}

请基于这些了解来辅助用户。不要主动暴露你知道这些信息，除非自然地需要引用。
回复简洁、自然，像一个了解用户的朋友。"""


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


def do_extract() -> dict:
    conv_text = format_conversation(session.messages)
    if not conv_text.strip():
        return {"extracted": 0, "entries": []}
    entries = extract_entries(conv_text)
    if entries:
        session.memory = add_entries(session.memory, entries)
        save_memory(session.memory)
    return {
        "extracted": len(entries),
        "entries": [{"category": e["category"], "content": e["content"]} for e in entries],
    }


@asynccontextmanager
async def lifespan(app: FastAPI):
    session.memory = load_memory()
    session.reset()
    yield


app = FastAPI(title="Memento", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    auto_extract: dict | None = None


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    user_input = req.message.strip()
    if not user_input:
        return ChatResponse(reply="")

    # 命令处理
    if user_input == "/memory":
        entries = sorted(session.memory["entries"], key=lambda e: e["confidence"], reverse=True)
        return ChatResponse(
            reply=f"当前记忆 ({len(entries)} 条):\n" + get_context_text(session.memory)
        )

    if user_input == "/clear":
        session.memory = {"entries": [], "meta": {"total_conversations": 0, "last_updated": ""}}
        save_memory(session.memory)
        session.reset()
        return ChatResponse(reply="[记忆已清空]")

    if user_input == "/quit":
        result = do_extract()
        session.reset()
        msg = f"[提取到 {result['extracted']} 条新记忆，会话已重置]"
        return ChatResponse(reply=msg, auto_extract=result)

    # 正常对话
    session.messages.append({"role": "user", "content": user_input})

    try:
        response = call_llm(session.messages)
    except Exception as e:
        session.messages.pop()
        return ChatResponse(reply=f"[调用失败: {e}]")

    session.messages.append({"role": "assistant", "content": response})
    session.turn_count += 1

    # 自动提取
    auto_extract = None
    if session.turn_count % EXTRACT_BATCH_SIZE == 0:
        auto_extract = do_extract()
        session.reset()

    return ChatResponse(reply=response, auto_extract=auto_extract)


@app.get("/api/memory")
def get_memory():
    entries = sorted(session.memory["entries"], key=lambda e: e["confidence"], reverse=True)
    return {
        "entries": entries,
        "meta": session.memory.get("meta", {}),
    }


@app.post("/api/extract")
def manual_extract():
    result = do_extract()
    session.reset()
    return result


if __name__ == "__main__":
    import uvicorn

    if not API_KEY:
        print("错误：未设置 DEEPSEEK_API_KEY，请在 .env 文件中配置。")
        exit(1)

    print("=== Memento 个人记忆助手 ===")
    print(f"模型: {MODEL}")
    print(f"已有记忆: {len(session.memory.get('entries', []))} 条")
    print("启动中... 浏览器将自动打开 http://localhost:8000")

    threading.Timer(1.5, lambda: webbrowser.open("http://localhost:8000")).start()
    uvicorn.run(app, host="0.0.0.0", port=8000)
