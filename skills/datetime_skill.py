"""Date and time skill for the personal agent."""

from datetime import datetime, timezone
from typing import Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .base_skill import BaseSkill


class DateTimeSkill(BaseSkill):
    """Skill that provides current date, time, and timezone information."""

    @property
    def name(self) -> str:
        return "datetime"

    @property
    def description(self) -> str:
        return "Get current date, time, weekday, or timezone-aware datetime."

    def execute(self, *, timezone_name: Optional[str] = None, format: Optional[str] = None) -> str:
        """Return the current date and time.

        Args:
            timezone_name: Optional IANA timezone name (e.g. 'Europe/London').
                           Defaults to UTC.
            format: Optional strftime format string.
                    Defaults to '%Y-%m-%d %H:%M:%S %Z'.

        Returns:
            Formatted datetime string.

        Raises:
            ValueError: If an unknown timezone name is provided.
        """
        fmt = format or "%Y-%m-%d %H:%M:%S %Z"
        if timezone_name:
            try:
                tz = ZoneInfo(timezone_name)
            except (ZoneInfoNotFoundError, KeyError) as exc:
                raise ValueError(f"Unknown timezone: {timezone_name!r}") from exc
            now = datetime.now(tz=tz)
        else:
            now = datetime.now(tz=timezone.utc)
        return now.strftime(fmt)
