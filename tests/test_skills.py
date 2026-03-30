"""Tests for the skills package and the Agent orchestrator."""

import math
import sys
import os
from datetime import datetime, timedelta, timezone

import pytest

# Ensure the repo root is on the path when running tests directly
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from skills.calculator_skill import CalculatorSkill
from skills.datetime_skill import DateTimeSkill
from skills.notes_skill import NotesSkill
from skills.reminder_skill import Reminder, ReminderSkill
from agent import Agent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _future_iso(days: int = 365 * 50) -> str:
    """Return an ISO-8601 UTC datetime string that is ``days`` in the future."""
    dt = datetime.now(tz=timezone.utc) + timedelta(days=days)
    return dt.isoformat()


# ---------------------------------------------------------------------------
# DateTimeSkill
# ---------------------------------------------------------------------------

class TestDateTimeSkill:
    def setup_method(self):
        self.skill = DateTimeSkill()

    def test_name_and_description(self):
        assert self.skill.name == "datetime"
        assert "date" in self.skill.description.lower() or "time" in self.skill.description.lower()

    def test_returns_string(self):
        result = self.skill.execute()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_utc_by_default(self):
        result = self.skill.execute()
        assert "UTC" in result

    def test_timezone(self):
        result = self.skill.execute(timezone_name="Europe/London")
        assert isinstance(result, str)

    def test_custom_format(self):
        result = self.skill.execute(format="%Y")
        assert result.isdigit()
        assert len(result) == 4

    def test_invalid_timezone_raises(self):
        with pytest.raises(ValueError, match="Unknown timezone"):
            self.skill.execute(timezone_name="Not/ATimezone")


# ---------------------------------------------------------------------------
# CalculatorSkill
# ---------------------------------------------------------------------------

class TestCalculatorSkill:
    def setup_method(self):
        self.skill = CalculatorSkill()

    def test_name_and_description(self):
        assert self.skill.name == "calculator"
        assert len(self.skill.description) > 0

    def test_addition(self):
        assert self.skill.execute(expression="2 + 3") == 5

    def test_subtraction(self):
        assert self.skill.execute(expression="10 - 4") == 6

    def test_multiplication(self):
        assert self.skill.execute(expression="3 * 7") == 21

    def test_division(self):
        assert self.skill.execute(expression="10 / 4") == 2.5

    def test_floor_division(self):
        assert self.skill.execute(expression="10 // 3") == 3

    def test_modulo(self):
        assert self.skill.execute(expression="10 % 3") == 1

    def test_power(self):
        assert self.skill.execute(expression="2 ** 10") == 1024

    def test_sqrt_function(self):
        assert self.skill.execute(expression="sqrt(9)") == 3.0

    def test_pi_constant(self):
        result = self.skill.execute(expression="pi")
        assert abs(result - math.pi) < 1e-10

    def test_unary_negation(self):
        assert self.skill.execute(expression="-5") == -5

    def test_nested_expression(self):
        result = self.skill.execute(expression="2 + 3 * sqrt(4)")
        assert abs(result - 8.0) < 1e-10

    def test_invalid_syntax_raises(self):
        with pytest.raises(ValueError, match="Invalid expression syntax"):
            self.skill.execute(expression="2 +* 3")

    def test_unknown_name_raises(self):
        with pytest.raises(ValueError, match="Unknown name"):
            self.skill.execute(expression="secret_var")

    def test_disallowed_import_raises(self):
        with pytest.raises(ValueError):
            self.skill.execute(expression="__import__('os')")


# ---------------------------------------------------------------------------
# NotesSkill
# ---------------------------------------------------------------------------

class TestNotesSkill:
    def setup_method(self):
        self.skill = NotesSkill()

    def test_name_and_description(self):
        assert self.skill.name == "notes"
        assert len(self.skill.description) > 0

    def test_list_empty(self):
        result = self.skill.execute(action="list")
        assert "No notes" in result

    def test_add_and_get(self):
        self.skill.execute(action="add", title="shopping", content="Milk, eggs")
        result = self.skill.execute(action="get", title="shopping")
        assert result == "Milk, eggs"

    def test_list_shows_titles(self):
        self.skill.execute(action="add", title="alpha", content="A")
        self.skill.execute(action="add", title="beta", content="B")
        result = self.skill.execute(action="list")
        assert "alpha" in result
        assert "beta" in result

    def test_update(self):
        self.skill.execute(action="add", title="memo", content="original")
        self.skill.execute(action="update", title="memo", content="updated")
        assert self.skill.execute(action="get", title="memo") == "updated"

    def test_delete(self):
        self.skill.execute(action="add", title="temp", content="x")
        self.skill.execute(action="delete", title="temp")
        result = self.skill.execute(action="list")
        assert "temp" not in result

    def test_add_duplicate_raises(self):
        self.skill.execute(action="add", title="dup", content="first")
        with pytest.raises(ValueError, match="already exists"):
            self.skill.execute(action="add", title="dup", content="second")

    def test_get_missing_raises(self):
        with pytest.raises(ValueError, match="not found"):
            self.skill.execute(action="get", title="ghost")

    def test_update_missing_raises(self):
        with pytest.raises(ValueError, match="not found"):
            self.skill.execute(action="update", title="ghost", content="x")

    def test_delete_missing_raises(self):
        with pytest.raises(ValueError, match="not found"):
            self.skill.execute(action="delete", title="ghost")

    def test_unknown_action_raises(self):
        with pytest.raises(ValueError, match="Unknown action"):
            self.skill.execute(action="frobnicate", title="x")

    def test_add_without_content_raises(self):
        with pytest.raises(ValueError, match="'content' is required"):
            self.skill.execute(action="add", title="x")

    def test_add_without_title_raises(self):
        with pytest.raises(ValueError, match="'title' is required"):
            self.skill.execute(action="add", content="x")


# ---------------------------------------------------------------------------
# ReminderSkill
# ---------------------------------------------------------------------------

class TestReminderSkill:
    def setup_method(self):
        self.skill = ReminderSkill()

    def test_name_and_description(self):
        assert self.skill.name == "reminder"
        assert len(self.skill.description) > 0

    def test_list_empty(self):
        result = self.skill.execute(action="list")
        assert "No reminders" in result

    def test_add_and_check(self):
        self.skill.execute(action="add", title="meeting", due=_future_iso())
        result = self.skill.execute(action="check", title="meeting")
        assert "meeting" in result
        assert "pending" in result.lower()

    def test_add_past_reminder_is_due(self):
        self.skill.execute(action="add", title="past", due="2000-01-01T00:00:00+00:00")
        result = self.skill.execute(action="check", title="past")
        assert "DUE" in result

    def test_list_shows_titles(self):
        self.skill.execute(action="add", title="a", due=_future_iso())
        result = self.skill.execute(action="list")
        assert "a" in result

    def test_due_action_no_due_reminders(self):
        self.skill.execute(action="add", title="future", due=_future_iso())
        result = self.skill.execute(action="due")
        assert "No reminders" in result

    def test_due_action_with_due_reminder(self):
        self.skill.execute(action="add", title="old", due="2000-06-15T12:00:00+00:00")
        result = self.skill.execute(action="due")
        assert "old" in result

    def test_delete(self):
        self.skill.execute(action="add", title="del_me", due=_future_iso())
        self.skill.execute(action="delete", title="del_me")
        result = self.skill.execute(action="list")
        assert "del_me" not in result

    def test_add_duplicate_raises(self):
        self.skill.execute(action="add", title="dup", due=_future_iso())
        with pytest.raises(ValueError, match="already exists"):
            self.skill.execute(action="add", title="dup", due=_future_iso(days=365 * 51))

    def test_add_invalid_due_raises(self):
        with pytest.raises(ValueError, match="Cannot parse"):
            self.skill.execute(action="add", title="bad", due="not-a-date")

    def test_check_missing_raises(self):
        with pytest.raises(ValueError, match="not found"):
            self.skill.execute(action="check", title="ghost")

    def test_delete_missing_raises(self):
        with pytest.raises(ValueError, match="not found"):
            self.skill.execute(action="delete", title="ghost")

    def test_unknown_action_raises(self):
        with pytest.raises(ValueError, match="Unknown action"):
            self.skill.execute(action="frobnicate", title="x")

    def test_invalid_timezone_raises(self):
        with pytest.raises(ValueError, match="Unknown timezone"):
            self.skill.execute(action="list", timezone_name="Fake/Zone")

    def test_add_naive_datetime_treated_as_utc(self):
        self.skill.execute(action="add", title="naive", due=(
            datetime.now(tz=timezone.utc) + timedelta(days=365 * 50)
        ).strftime("%Y-%m-%dT%H:%M:%S"))
        result = self.skill.execute(action="check", title="naive")
        assert "naive" in result


# ---------------------------------------------------------------------------
# Reminder dataclass
# ---------------------------------------------------------------------------

class TestReminder:
    def test_is_due_past(self):
        from datetime import datetime, timezone
        r = Reminder("x", datetime(2000, 1, 1, tzinfo=timezone.utc))
        assert r.is_due()

    def test_is_not_due_future(self):
        from datetime import datetime, timezone
        r = Reminder("x", datetime.now(tz=timezone.utc) + timedelta(days=365 * 50))
        assert not r.is_due()

    def test_str(self):
        from datetime import datetime, timezone
        r = Reminder("check", datetime(2026, 4, 1, 9, 0, 0, tzinfo=timezone.utc), "important")
        s = str(r)
        assert "check" in s
        assert "important" in s


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class TestAgent:
    def setup_method(self):
        self.agent = Agent()

    def test_default_skills_registered(self):
        assert "datetime" in self.agent.skills
        assert "calculator" in self.agent.skills
        assert "notes" in self.agent.skills
        assert "reminder" in self.agent.skills

    def test_help_output(self):
        h = self.agent.help()
        assert "datetime" in h
        assert "calculator" in h

    def test_run_calculator(self):
        result = self.agent.run("calculator", expression="6 * 7")
        assert result == 42

    def test_run_datetime(self):
        result = self.agent.run("datetime")
        assert isinstance(result, str)

    def test_run_unknown_skill_raises(self):
        with pytest.raises(ValueError, match="Unknown skill"):
            self.agent.run("nonexistent")

    def test_register_custom_skill(self):
        from skills.base_skill import BaseSkill

        class PingSkill(BaseSkill):
            @property
            def name(self):
                return "ping"
            @property
            def description(self):
                return "Returns pong."
            def execute(self, **kwargs):
                return "pong"

        self.agent.register(PingSkill())
        assert self.agent.run("ping") == "pong"

    def test_register_duplicate_raises(self):
        from skills.base_skill import BaseSkill

        class CalcDup(BaseSkill):
            @property
            def name(self):
                return "calculator"
            @property
            def description(self):
                return "duplicate"
            def execute(self, **kwargs):
                return 0

        with pytest.raises(ValueError, match="already registered"):
            self.agent.register(CalcDup())

    def test_unregister_skill(self):
        self.agent.unregister("calculator")
        assert "calculator" not in self.agent.skills

    def test_unregister_unknown_raises(self):
        with pytest.raises(ValueError, match="No skill named"):
            self.agent.unregister("nosuchskill")
