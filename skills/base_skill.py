"""Base class for all agent skills."""

from abc import ABC, abstractmethod
from typing import Any


class BaseSkill(ABC):
    """Abstract base class that all skills must inherit from."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this skill."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Return a short description of what this skill does."""

    @abstractmethod
    def execute(self, **kwargs: Any) -> Any:
        """Execute the skill with the provided keyword arguments."""
