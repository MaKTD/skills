"""Personal agent – orchestrates a collection of skills."""

from __future__ import annotations

from typing import Any

from skills.base_skill import BaseSkill
from skills.calculator_skill import CalculatorSkill
from skills.datetime_skill import DateTimeSkill
from skills.notes_skill import NotesSkill
from skills.reminder_skill import ReminderSkill


class Agent:
    """A simple personal agent that delegates work to registered skills."""

    def __init__(self) -> None:
        self._skills: dict[str, BaseSkill] = {}
        for skill in (DateTimeSkill(), CalculatorSkill(), NotesSkill(), ReminderSkill()):
            self.register(skill)

    # ------------------------------------------------------------------
    # Skill management
    # ------------------------------------------------------------------

    def register(self, skill: BaseSkill) -> None:
        """Register a skill with the agent.

        Args:
            skill: A :class:`BaseSkill` instance to register.

        Raises:
            ValueError: If a skill with the same name is already registered.
        """
        if skill.name in self._skills:
            raise ValueError(
                f"A skill named {skill.name!r} is already registered. "
                "Unregister it first or use a different name."
            )
        self._skills[skill.name] = skill

    def unregister(self, skill_name: str) -> None:
        """Remove a skill by name.

        Args:
            skill_name: The name of the skill to remove.

        Raises:
            ValueError: If the skill is not registered.
        """
        if skill_name not in self._skills:
            raise ValueError(f"No skill named {skill_name!r} is registered.")
        del self._skills[skill_name]

    @property
    def skills(self) -> list[str]:
        """Return a sorted list of registered skill names."""
        return sorted(self._skills)

    def help(self) -> str:
        """Return a human-readable summary of all registered skills."""
        if not self._skills:
            return "No skills registered."
        lines = ["Available skills:"]
        for name in self.skills:
            skill = self._skills[name]
            lines.append(f"  {name}: {skill.description}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def run(self, skill_name: str, **kwargs: Any) -> Any:
        """Execute a skill by name.

        Args:
            skill_name: The name of the skill to execute.
            **kwargs: Arguments forwarded to the skill's ``execute`` method.

        Returns:
            Whatever the skill returns.

        Raises:
            ValueError: If no skill with the given name is registered.
        """
        if skill_name not in self._skills:
            raise ValueError(
                f"Unknown skill {skill_name!r}. "
                f"Available skills: {', '.join(self.skills) or 'none'}."
            )
        return self._skills[skill_name].execute(**kwargs)


# ---------------------------------------------------------------------------
# Simple interactive REPL (entry-point)
# ---------------------------------------------------------------------------

def _repl(agent: Agent) -> None:  # pragma: no cover
    """Run a minimal command-line REPL for the agent."""
    print("Personal Agent  (type 'help' for available skills, 'quit' to exit)\n")
    while True:
        try:
            raw = input("agent> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not raw:
            continue
        if raw.lower() in {"quit", "exit", "q"}:
            print("Goodbye.")
            break
        if raw.lower() == "help":
            print(agent.help())
            continue

        # Parse: skill_name key=value key=value …
        parts = raw.split()
        skill_name = parts[0]
        kwargs: dict[str, Any] = {}
        for part in parts[1:]:
            if "=" in part:
                k, _, v = part.partition("=")
                kwargs[k] = v
            else:
                # Treat bare words as positional-ish: append to 'expression' or 'action'
                if "action" not in kwargs:
                    kwargs["action"] = part
                else:
                    kwargs.setdefault("expression", part)

        try:
            result = agent.run(skill_name, **kwargs)
            print(result)
        except ValueError as exc:
            print(f"Error: {exc}")


if __name__ == "__main__":
    _repl(Agent())
