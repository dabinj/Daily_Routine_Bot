from __future__ import annotations

import re


TIME_RE = re.compile(
    r"(?P<meridiem>오전|오후|am|pm)?\s*"
    r"(?P<hour>[01]?\d|2[0-3])"
    r"(?:[:시]\s*(?P<minute>[0-5]\d)?)?"
    r"\s*(?:분)?",
    re.IGNORECASE,
)


def parse_time_to_hhmm(value: str, preference: str | None = None) -> str | None:
    match = TIME_RE.search(value.strip())
    if not match:
        return None

    hour = int(match.group("hour"))
    minute = int(match.group("minute") or 0)
    meridiem = (match.group("meridiem") or "").lower()

    if meridiem in {"오후", "pm"} and hour < 12:
        hour += 12
    elif meridiem in {"오전", "am"} and hour == 12:
        hour = 0
    elif not meridiem and preference == "evening" and 1 <= hour <= 11:
        hour += 12

    if not 0 <= hour <= 23:
        return None
    return f"{hour:02d}:{minute:02d}"
