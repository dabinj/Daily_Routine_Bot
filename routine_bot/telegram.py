from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def http_json(url: str, params: dict[str, Any] | None = None, timeout: int = 30) -> dict[str, Any]:
    data = None
    headers = {"User-Agent": "DailyRoutineBot/0.1"}
    if params is not None:
        data = urlencode(params).encode("utf-8")
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    req = Request(url, data=data, headers=headers)
    try:
        with urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {body}") from exc


def telegram_call(token: str, method: str, params: dict[str, Any] | None = None, timeout: int = 30) -> dict[str, Any]:
    return http_json(f"https://api.telegram.org/bot{token}/{method}", params=params, timeout=timeout)


def send_message(token: str, chat_id: int, text: str) -> None:
    result = telegram_call(token, "sendMessage", {"chat_id": str(chat_id), "text": text})
    if not result.get("ok"):
        raise RuntimeError(result.get("description", "sendMessage failed"))

