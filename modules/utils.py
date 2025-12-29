import html
import json
import os


def esc(text: str) -> str:
    return html.escape(text) if text else ""


def load_users():
    raw = os.getenv("USERS")
    if not raw:
        raise RuntimeError("USERS 未設定")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        raise RuntimeError("USERS の形式が不正です（JSON形式）")
