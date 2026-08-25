from __future__ import annotations

from datetime import datetime
from typing import Any

WEEKDAY_KEYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def weekday_key(now: datetime) -> str:
    return WEEKDAY_KEYS[now.weekday()]


def due_questions(schedule: dict[str, Any], state: dict[str, Any], now: datetime) -> list[dict[str, Any]]:
    if state.get("paused"):
        return []

    today = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M")
    weekday = weekday_key(now)
    sent = state.setdefault("sent_questions", {})
    questions = []

    for question in schedule.get("questions", []):
        if weekday not in question.get("weekdays", WEEKDAY_KEYS):
            continue
        send_time = question.get("time")
        if not send_time or send_time > current_time:
            continue
        sent_key = f"{today}:{question['field']}"
        if sent.get(sent_key):
            continue
        questions.append(question)

    return questions


def mark_sent(state: dict[str, Any], question: dict[str, Any], now: datetime) -> None:
    sent = state.setdefault("sent_questions", {})
    sent[f"{now.strftime('%Y-%m-%d')}:{question['field']}"] = now.isoformat()

