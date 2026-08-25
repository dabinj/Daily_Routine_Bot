from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Any


def help_text() -> str:
    return (
        "Daily Routine Bot\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "/start - 이 대화방 등록\n"
        "/today - 오늘 기록 조회\n"
        "/week - 최근 7일 요약\n"
        "/fields - 기록 항목 보기\n"
        "/record <항목> <내용> - 수동 기록\n"
        "/skip - 현재 질문 건너뛰기\n"
        "/cancel - 현재 질문 취소\n"
        "/pause - 스케줄 질문 일시 중지\n"
        "/resume - 스케줄 질문 재개\n"
        "/status - 봇 상태 확인"
    )


def question_text(question: dict[str, Any]) -> str:
    lines = [
        "Daily Routine",
        "━━━━━━━━━━━━━━━━━━━━",
        question.get("message", question.get("label", "루틴을 입력해주세요.")),
    ]
    options = question.get("options") or []
    if options:
        lines.append("")
        for index, option in enumerate(options, start=1):
            lines.append(f"{index}. {option}")
        lines.append("")
        lines.append("번호 또는 직접 입력으로 답해주세요.")
    else:
        lines.append("")
        lines.append("자유롭게 입력해주세요.")
    return "\n".join(lines)


def question_keyboard(question: dict[str, Any]) -> dict[str, Any] | None:
    options = question.get("options") or []
    if not options:
        return None
    rows = [[{"text": str(option)}] for option in options]
    return {
        "keyboard": rows,
        "one_time_keyboard": True,
        "resize_keyboard": True,
        "is_persistent": False,
    }


def remove_keyboard() -> dict[str, Any]:
    return {"remove_keyboard": True}


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
