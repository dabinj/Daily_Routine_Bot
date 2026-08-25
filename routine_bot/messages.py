from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Any


MENU_COMMANDS = {
    "오늘 기록": "/today",
    "최근 7일": "/week",
    "상태": "/status",
    "항목 보기": "/fields",
    "도움말": "/help",
    "일시 중지": "/pause",
    "다시 시작": "/resume",
    "질문 건너뛰기": "/skip",
    "취소": "/cancel",
}


def help_text() -> str:
    return (
        "Daily Routine Bot\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "버튼으로 조회와 상태 변경을 할 수 있습니다.\n"
        "직접 기록: /record <항목> <내용>\n"
        "예: /record lunch_menu 김치찌개"
    )


def question_text(question: dict[str, Any]) -> str:
    lines = [
        "Daily Routine",
        "━━━━━━━━━━━━━━━━━━━━",
        question.get("label", "루틴 기록"),
        "",
        question.get("message", question.get("label", "루틴을 입력해주세요.")),
    ]
    options = question.get("options") or []
    if options:
        lines.append("")
        lines.append("버튼으로 선택하거나 직접 입력해주세요.")
    else:
        lines.append("")
        lines.append("직접 입력해주세요.")
    return "\n".join(lines)


def command_from_button(text: str) -> str:
    return MENU_COMMANDS.get(text.strip(), text.strip())


def chunked(items: list[str], columns: int) -> list[list[dict[str, str]]]:
    rows: list[list[dict[str, str]]] = []
    for index in range(0, len(items), columns):
        rows.append([{"text": item} for item in items[index : index + columns]])
    return rows


def main_menu_keyboard() -> dict[str, Any]:
    return {
        "keyboard": [
            [{"text": "오늘 기록"}, {"text": "최근 7일"}],
            [{"text": "상태"}, {"text": "항목 보기"}],
            [{"text": "일시 중지"}, {"text": "다시 시작"}],
        ],
        "resize_keyboard": True,
        "is_persistent": True,
    }


def question_keyboard(question: dict[str, Any]) -> dict[str, Any] | None:
    options = question.get("options") or []
    columns = int(question.get("keyboard_columns") or 2)
    rows = chunked([str(option) for option in options], columns) if options else []
    rows.append([{"text": "질문 건너뛰기"}, {"text": "취소"}])
    return {
        "keyboard": rows,
        "resize_keyboard": True,
        "one_time_keyboard": False,
        "is_persistent": True,
    }


def remove_keyboard() -> dict[str, Any]:
    return {"remove_keyboard": True}


def after_answer_text(question: dict[str, Any], value: str) -> str:
    rules = question.get("after_answer") or {}
    if not isinstance(rules, dict):
        return ""
    message = rules.get(value) or rules.get("default")
    return str(message).strip() if message else ""


def recorded_text(label: str, value: str, feedback: str = "") -> str:
    lines = [
        "기록했습니다.",
        "━━━━━━━━━━━━━━━━━━━━",
        f"{label}: {value}",
    ]
    if feedback:
        lines.extend(["", feedback])
    return "\n".join(lines)


def today_text(entry_date: str, entries: list[dict[str, Any]]) -> str:
    if not entries:
        return f"오늘 루틴\n━━━━━━━━━━━━━━━━━━━━\n{entry_date} 기록이 아직 없습니다."
    lines = [f"오늘 루틴", "━━━━━━━━━━━━━━━━━━━━", entry_date]
    for entry in entries:
        lines.append(f"- {entry['label']}: {entry['value']}")
    return "\n".join(lines)


def week_text(entries: list[dict[str, Any]]) -> str:
    if not entries:
        return "최근 7일 기록이 없습니다."
    by_date: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entry in entries:
        by_date[entry["entry_date"]].append(entry)

    lines = ["최근 7일 루틴", "━━━━━━━━━━━━━━━━━━━━"]
    for entry_date in sorted(by_date, reverse=True):
        lines.append("")
        lines.append(entry_date)
        for entry in by_date[entry_date]:
            lines.append(f"- {entry['label']}: {entry['value']}")
    return "\n".join(lines)


def status_text(state: dict[str, Any]) -> str:
    paused = "일시 중지" if state.get("paused") else "운영 중"
    pending = state.get("pending_question")
    pending_label = pending.get("label") if isinstance(pending, dict) else "없음"
    return (
        "Routine Bot Status\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"상태: {paused}\n"
        f"대기 질문: {pending_label}\n"
        f"확인 시각: {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M')}"
    )


def fields_text(schedule: dict[str, Any]) -> str:
    lines = ["기록 항목", "━━━━━━━━━━━━━━━━━━━━"]
    for field, label in schedule.get("labels", {}).items():
        lines.append(f"- {field}: {label}")
    lines.append("")
    lines.append("수동 기록 예: /record lunch_menu 김치찌개")
    return "\n".join(lines)
