from __future__ import annotations

from datetime import datetime
from typing import Any

from .timeparse import parse_time_to_hhmm

WEEKDAY_KEYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def weekday_key(now: datetime) -> str:
    return WEEKDAY_KEYS[now.weekday()]


def entries_by_field(entries: list[dict[str, Any]]) -> dict[str, str]:
    return {str(entry["field"]): str(entry["value"]) for entry in entries}


def condition_matches(condition: dict[str, Any], entries: dict[str, str]) -> bool:
    field = condition.get("field")
    if not field or field not in entries:
        return False

    value = entries[field].strip()
    if "equals" in condition:
        return value == str(condition["equals"])
    if "in" in condition:
        return value in {str(item) for item in condition["in"]}
    if "not_in" in condition:
        return value not in {str(item) for item in condition["not_in"]}
    if condition.get("exists"):
        return bool(value)
    return True


def conditions_match(question: dict[str, Any], entries: dict[str, str]) -> bool:
    for condition in question.get("requires", []):
        if not condition_matches(condition, entries):
            return False
    return True


def question_send_time(question: dict[str, Any], entries: dict[str, str]) -> str | None:
    source_field = question.get("dynamic_time_from")
    if source_field:
        source_value = entries.get(str(source_field))
        if not source_value:
            return None
        return parse_time_to_hhmm(source_value, question.get("dynamic_time_preference"))
    return question.get("time")


def due_questions(
    schedule: dict[str, Any],
    state: dict[str, Any],
    now: datetime,
    entries: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    if state.get("paused"):
        return []

    today = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M")
    weekday = weekday_key(now)
    sent = state.setdefault("sent_questions", {})
    entry_map = entries_by_field(entries or [])
    questions = []

    for question in schedule.get("questions", []):
        if weekday not in question.get("weekdays", WEEKDAY_KEYS):
            continue
        if question["field"] in entry_map:
            continue
        if not conditions_match(question, entry_map):
            continue
        send_time = question_send_time(question, entry_map)
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
