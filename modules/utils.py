import html
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo


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


def format_japan_datetime(row_datetime: datetime | None):
    if not row_datetime:
        return None
    if row_datetime.tzinfo is None:
        from datetime import timezone

        row_datetime = row_datetime.replace(tzinfo=timezone.utc)
    return row_datetime.astimezone(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d %H:%M")
