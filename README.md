# skills

Personal agent skills collection – a lightweight Python library of reusable **skills** that can be plugged into a personal AI agent.

## Overview

Each skill is an independent module that inherits from `BaseSkill` and exposes a single `execute(**kwargs)` method.  The `Agent` class acts as an orchestrator: it registers skills and dispatches work to them by name.

### Built-in skills

| Skill | Description |
|-------|-------------|
| `datetime` | Return current date/time, optionally in a specific timezone or format |
| `calculator` | Safely evaluate mathematical expressions (supports `sqrt`, `sin`, `cos`, `log`, `pi`, `e`, …) |
| `notes` | Create, read, update, delete and list personal notes (in-memory) |
| `reminder` | Set time-based reminders and query which ones are currently due |

## Quick start

```python
from agent import Agent

agent = Agent()

# What skills are available?
print(agent.help())

# Ask the datetime skill for the current time in Tokyo
print(agent.run("datetime", timezone_name="Asia/Tokyo"))

# Evaluate a math expression
print(agent.run("calculator", expression="sqrt(2) * pi"))

# Manage notes
agent.run("notes", action="add", title="ideas", content="Build something cool")
print(agent.run("notes", action="get", title="ideas"))

# Set a reminder
agent.run("reminder", action="add", title="dentist", due="2026-06-01T09:00:00+00:00")
print(agent.run("reminder", action="list"))
```

### Interactive REPL

```bash
python agent.py
```

## Adding a custom skill

```python
from skills.base_skill import BaseSkill
from agent import Agent

class GreetSkill(BaseSkill):
    @property
    def name(self):
        return "greet"

    @property
    def description(self):
        return "Greet someone by name."

    def execute(self, *, name="World"):
        return f"Hello, {name}!"

agent = Agent()
agent.register(GreetSkill())
print(agent.run("greet", name="Alice"))  # Hello, Alice!
```

## Running the tests

```bash
pip install -r requirements.txt
pytest tests/
```

