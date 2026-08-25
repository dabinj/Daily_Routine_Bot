from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from .config import load_json, load_settings, read_secret, save_json
from .messages import (
    fields_text,
    help_text,
    question_keyboard,
    question_text,
    remove_keyboard,
    status_text,
    today_text,
    week_text,
)
from .schedule import due_questions, mark_sent
from .storage import get_day_entries, get_recent_entries, init_db, upsert_entry
from .telegram import send_message, telegram_call

KST = ZoneInfo("Asia/Seoul")


def today_key() -> str:
    return datetime.now(KST).strftime("%Y-%m-%d")


def normalize_answer(question: dict, text: str) -> str:
    value = text.strip()
    options = question.get("options") or []
    if value.isdigit() and options:
        index = int(value)
        if 1 <= index <= len(options):
            return str(options[index - 1])
    return value


def handle_message(token: str, chat_id: int, text: str, state: dict, schedule: dict) -> bool:
    settings = load_settings()
    command = text.strip()

    if command == "/start":
        settings.telegram_chat_path.write_text(str(chat_id) + "\n", encoding="utf-8")
        send_message(token, chat_id, "Daily Routine Bot 등록이 완료되었습니다.\n\n" + help_text())
        return True

    if command == "/help":
        send_message(token, chat_id, help_text())
        return False

    if command == "/pause":
        state["paused"] = True
        send_message(token, chat_id, "스케줄 질문을 일시 중지했습니다. 다시 켜려면 /resume")
        return True

    if command == "/resume":
        state["paused"] = False
        send_message(token, chat_id, "스케줄 질문을 재개했습니다.")
        return True

    if command == "/status":
        send_message(token, chat_id, status_text(state))
        return False

    if command == "/fields":
        send_message(token, chat_id, fields_text(schedule))
        return False

    if command == "/today":
        send_message(token, chat_id, today_text(today_key(), get_day_entries(settings.db_path, today_key())))
        return False

    if command == "/week":
        send_message(token, chat_id, week_text(get_recent_entries(settings.db_path, 7, today_key())))
        return False

    if command in {"/skip", "/cancel", "/cancle"}:
        pending = state.pop("pending_question", None)
        if pending:
            upsert_entry(settings.db_path, today_key(), pending["field"], pending["label"], "skip", "skip", pending.get("asked_at"))
            send_message(token, chat_id, f"{pending['label']} 질문을 건너뛰었습니다.", remove_keyboard())
            return True
        send_message(token, chat_id, "대기 중인 질문이 없습니다.")
        return False

    if command.startswith("/record "):
        parts = command.split(maxsplit=2)
        if len(parts) < 3:
            send_message(token, chat_id, "사용법: /record <항목> <내용>")
            return False
        field = parts[1]
        label = schedule.get("labels", {}).get(field, field)
        upsert_entry(settings.db_path, today_key(), field, label, parts[2], "manual")
        send_message(token, chat_id, f"기록했습니다.\n{label}: {parts[2]}")
        return True

    pending = state.get("pending_question")
    if isinstance(pending, dict):
        value = normalize_answer(pending, text)
        upsert_entry(settings.db_path, today_key(), pending["field"], pending["label"], value, "scheduled", pending.get("asked_at"))
        state.pop("pending_question", None)
        send_message(token, chat_id, f"기록했습니다.\n{pending['label']}: {value}", remove_keyboard())
        return True

    send_message(token, chat_id, "알 수 없는 입력입니다. /help")
    return False


def send_due_questions(token: str, chat_id: int, state: dict, schedule: dict) -> bool:
    settings = load_settings()
    now = datetime.now(KST)
    entries = get_day_entries(settings.db_path, today_key())
    questions = due_questions(schedule, state, now, entries)
    if not questions or state.get("pending_question"):
        return False

    question = questions[0]
    state["pending_question"] = {
        "field": question["field"],
        "label": question["label"],
        "options": question.get("options", []),
        "asked_at": now.isoformat(),
    }
    mark_sent(state, question, now)
    send_message(token, chat_id, question_text(question), question_keyboard(question))
    return True


def command_poll(args: argparse.Namespace) -> int:
    settings = load_settings()
    init_db(settings.db_path)
    token = read_secret(settings.telegram_key_path)
    state = load_json(settings.state_path, {})
    schedule = load_json(settings.schedule_path, {"questions": [], "labels": {}})
    chat_id = int(read_secret(settings.telegram_chat_path)) if settings.telegram_chat_path.exists() else None
    print("routine_bot=polling")

    while True:
        try:
            if chat_id:
                if send_due_questions(token, chat_id, state, schedule):
                    save_json(settings.state_path, state)

            params = {"timeout": args.timeout, "allowed_updates": json.dumps(["message"])}
            if state.get("telegram_update_offset"):
                params["offset"] = state["telegram_update_offset"]
            updates = telegram_call(token, "getUpdates", params, timeout=args.timeout + 10)
            for update in updates.get("result", []):
                state["telegram_update_offset"] = int(update["update_id"]) + 1
                save_json(settings.state_path, state)
                message = update.get("message") or {}
                text = message.get("text")
                chat = message.get("chat") or {}
                if not text or not chat.get("id"):
                    continue
                chat_id = int(chat["id"])
                changed = handle_message(token, chat_id, text, state, schedule)
                if changed:
                    save_json(settings.state_path, state)
            if updates.get("result"):
                save_json(settings.state_path, state)
        except KeyboardInterrupt:
            return 0
        except Exception as exc:
            print(f"routine_bot_error={exc}", file=sys.stderr)
            time.sleep(args.sleep)


def command_init_db(_args: argparse.Namespace) -> int:
    settings = load_settings()
    init_db(settings.db_path)
    print(f"db_initialized={settings.db_path}")
    return 0


def command_help_text(_args: argparse.Namespace) -> int:
    print(help_text())
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="routine-bot")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init-db").set_defaults(func=command_init_db)
    sub.add_parser("help-text").set_defaults(func=command_help_text)
    poll = sub.add_parser("poll")
    poll.add_argument("--timeout", type=int, default=25)
    poll.add_argument("--sleep", type=float, default=2.0)
    poll.set_defaults(func=command_poll)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
