"""Reminder skill for the personal agent."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .base_skill import BaseSkill


class Reminder:
    """Represents a single reminder entry."""

    def __init__(self, title: str, due: datetime, message: str = "") -> None:
        self.title = title
        self.due = due
        self.message = message

    def is_due(self, as_of: Optional[datetime] = None) -> bool:
        """Return True if this reminder is at or past its due time."""
        reference = as_of or datetime.now(tz=timezone.utc)
        return reference >= self.due

    def __str__(self) -> str:
        due_str = self.due.strftime("%Y-%m-%d %H:%M:%S %Z")
        msg_part = f" — {self.message}" if self.message else ""
        return f"[{self.title}] due {due_str}{msg_part}"


class ReminderSkill(BaseSkill):
    """Skill that manages time-based reminders."""

    def __init__(self) -> None:
        self._reminders: dict[str, Reminder] = {}

    @property
    def name(self) -> str:
        return "reminder"

    @property
    def description(self) -> str:
        return (
            "Set, list, check, and delete reminders. "
            "Due times must be ISO-8601 strings (e.g. '2026-04-01T09:00:00+00:00')."
        )

    def execute(
        self,
        *,
        action: str,
        title: Optional[str] = None,
        due: Optional[str] = None,
        message: str = "",
        timezone_name: Optional[str] = None,
    ) -> str:
        """Manage reminders.

        Args:
            action: One of 'add', 'list', 'check', 'delete', 'due'.
            title: Reminder title (required for add/check/delete).
            due: ISO-8601 due datetime string (required for add).
            message: Optional extra message for the reminder.
            timezone_name: Optional IANA timezone for displaying times in 'list'/'check'.

        Returns:
            A string describing the result.

        Raises:
            ValueError: If required arguments are missing, action is unknown,
                        or the due string cannot be parsed.
        """
        action = action.lower().strip()

        tz = timezone.utc
        if timezone_name:
            try:
                tz = ZoneInfo(timezone_name)  # type: ignore[assignment]
            except (ZoneInfoNotFoundError, KeyError) as exc:
                raise ValueError(f"Unknown timezone: {timezone_name!r}") from exc

        if action == "list":
            if not self._reminders:
                return "No reminders set."
            lines = [str(r) for r in sorted(self._reminders.values(), key=lambda r: r.due)]
            return "Reminders:\n" + "\n".join(f"- {line}" for line in lines)

        if action == "due":
            now = datetime.now(tz=timezone.utc)
            due_now = [r for r in self._reminders.values() if r.is_due(as_of=now)]
            if not due_now:
                return "No reminders are currently due."
            lines = [str(r) for r in sorted(due_now, key=lambda r: r.due)]
            return "Due reminders:\n" + "\n".join(f"- {line}" for line in lines)

        if title is None:
            raise ValueError(f"'title' is required for action '{action}'")

        if action == "add":
            if due is None:
                raise ValueError("'due' is required for action 'add'")
            try:
                due_dt = datetime.fromisoformat(due)
            except ValueError as exc:
                raise ValueError(f"Cannot parse due time {due!r}: {exc}") from exc
            if due_dt.tzinfo is None:
                due_dt = due_dt.replace(tzinfo=timezone.utc)
            if title in self._reminders:
                raise ValueError(
                    f"Reminder {title!r} already exists. Delete it first to re-add."
                )
            self._reminders[title] = Reminder(title=title, due=due_dt, message=message)
            return f"Reminder {title!r} set for {due_dt.strftime('%Y-%m-%d %H:%M:%S %Z')}."

        if action == "check":
            if title not in self._reminders:
                raise ValueError(f"Reminder {title!r} not found.")
            reminder = self._reminders[title]
            status = "DUE" if reminder.is_due() else "pending"
            return f"{reminder} [{status}]"

        if action == "delete":
            if title not in self._reminders:
                raise ValueError(f"Reminder {title!r} not found.")
            del self._reminders[title]
            return f"Reminder {title!r} deleted."

        raise ValueError(
            f"Unknown action {action!r}. Valid actions: add, list, check, delete, due."
        )
