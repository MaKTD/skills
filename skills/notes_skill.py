"""Notes skill for the personal agent."""

from typing import Optional

from .base_skill import BaseSkill


class NotesSkill(BaseSkill):
    """Skill that manages a simple in-memory collection of named notes."""

    def __init__(self) -> None:
        self._notes: dict[str, str] = {}

    @property
    def name(self) -> str:
        return "notes"

    @property
    def description(self) -> str:
        return "Create, read, update, delete, and list personal notes."

    def execute(
        self,
        *,
        action: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
    ) -> str:
        """Manage notes.

        Args:
            action: One of 'add', 'get', 'update', 'delete', 'list'.
            title: The note title (required for add/get/update/delete).
            content: The note content (required for add/update).

        Returns:
            A string describing the result of the operation.

        Raises:
            ValueError: If required arguments are missing or action is unknown.
        """
        action = action.lower().strip()

        if action == "list":
            if not self._notes:
                return "No notes found."
            return "Notes:\n" + "\n".join(f"- {t}" for t in sorted(self._notes))

        if title is None:
            raise ValueError(f"'title' is required for action '{action}'")

        if action == "add":
            if content is None:
                raise ValueError("'content' is required for action 'add'")
            if title in self._notes:
                raise ValueError(f"Note {title!r} already exists. Use 'update' to change it.")
            self._notes[title] = content
            return f"Note {title!r} added."

        if action == "get":
            if title not in self._notes:
                raise ValueError(f"Note {title!r} not found.")
            return self._notes[title]

        if action == "update":
            if content is None:
                raise ValueError("'content' is required for action 'update'")
            if title not in self._notes:
                raise ValueError(f"Note {title!r} not found. Use 'add' to create it.")
            self._notes[title] = content
            return f"Note {title!r} updated."

        if action == "delete":
            if title not in self._notes:
                raise ValueError(f"Note {title!r} not found.")
            del self._notes[title]
            return f"Note {title!r} deleted."

        raise ValueError(
            f"Unknown action {action!r}. Valid actions: add, get, update, delete, list."
        )
