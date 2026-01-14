"""
State management for Grok Code's Ralph Wiggum Loop.
Provides persistent task tracking across tool calls.
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

# State directory name
STATE_DIR_NAME = ".grokcode"

# Default task plan template
TASK_PLAN_TEMPLATE = """# Task Plan

## Current Goal
{goal}

## Tasks
{tasks}

## Notes
- Created: {created}
- Last updated: {updated}
"""

TASK_ITEM_TEMPLATE = "- [{status}] {description}"


class TaskPlan:
    """Manages a task plan with checkable items."""

    def __init__(self, goal: str = "", tasks: list[dict] | None = None):
        self.goal = goal
        self.tasks = tasks or []
        self.created = datetime.now().isoformat()
        self.updated = self.created

    def add_task(self, description: str, status: str = " ") -> int:
        """Add a task. Returns the task index."""
        self.tasks.append({"description": description, "status": status})
        self.updated = datetime.now().isoformat()
        return len(self.tasks) - 1

    def update_task(self, index: int, status: str) -> bool:
        """Update task status. Status: ' ' (pending), 'x' (done), '~' (in progress)."""
        if 0 <= index < len(self.tasks):
            self.tasks[index]["status"] = status
            self.updated = datetime.now().isoformat()
            return True
        return False

    def get_next_pending(self) -> int | None:
        """Get index of next pending task."""
        for i, task in enumerate(self.tasks):
            if task["status"] == " ":
                return i
        return None

    def to_markdown(self) -> str:
        """Convert to markdown format."""
        task_lines = []
        for i, task in enumerate(self.tasks):
            status = task["status"]
            desc = task["description"]
            task_lines.append(f"- [{status}] ({i}) {desc}")

        return TASK_PLAN_TEMPLATE.format(
            goal=self.goal or "(No goal set)",
            tasks="\n".join(task_lines) if task_lines else "(No tasks)",
            created=self.created,
            updated=self.updated
        )

    @classmethod
    def from_markdown(cls, content: str) -> "TaskPlan":
        """Parse a task plan from markdown."""
        plan = cls()

        # Extract goal
        goal_match = re.search(r"## Current Goal\n(.+?)(?=\n##|\Z)", content, re.DOTALL)
        if goal_match:
            plan.goal = goal_match.group(1).strip()

        # Extract tasks
        task_pattern = r"- \[(.)\] (?:\((\d+)\) )?(.+)"
        for match in re.finditer(task_pattern, content):
            status = match.group(1)
            description = match.group(3).strip()
            plan.tasks.append({"description": description, "status": status})

        # Extract timestamps
        created_match = re.search(r"Created: (.+)", content)
        if created_match:
            plan.created = created_match.group(1).strip()

        updated_match = re.search(r"Last updated: (.+)", content)
        if updated_match:
            plan.updated = updated_match.group(1).strip()

        return plan

    def summary(self) -> str:
        """Get a brief summary for injection into prompts."""
        total = len(self.tasks)
        done = sum(1 for t in self.tasks if t["status"] == "x")
        in_progress = sum(1 for t in self.tasks if t["status"] == "~")
        pending = total - done - in_progress

        lines = [f"**Goal**: {self.goal}" if self.goal else "**Goal**: (none set)"]
        lines.append(f"**Progress**: {done}/{total} done, {in_progress} in progress, {pending} pending")

        if self.tasks:
            lines.append("**Tasks**:")
            for i, task in enumerate(self.tasks):
                marker = {"x": "✓", "~": "→", " ": "○"}.get(task["status"], "?")
                lines.append(f"  {marker} ({i}) {task['description']}")

        return "\n".join(lines)


class StateManager:
    """Manages the .grokcode state directory and files."""

    def __init__(self, base_dir: str | Path | None = None):
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.state_dir = self.base_dir / STATE_DIR_NAME
        self.task_plan_file = self.state_dir / "task_plan.md"
        self.notes_file = self.state_dir / "notes.md"
        self._plan: TaskPlan | None = None

    def ensure_state_dir(self) -> Path:
        """Create state directory if it doesn't exist."""
        self.state_dir.mkdir(exist_ok=True)
        return self.state_dir

    def has_active_plan(self) -> bool:
        """Check if there's an active task plan."""
        return self.task_plan_file.exists()

    def load_plan(self) -> TaskPlan | None:
        """Load the current task plan."""
        if self.task_plan_file.exists():
            content = self.task_plan_file.read_text(encoding="utf-8")
            self._plan = TaskPlan.from_markdown(content)
            return self._plan
        return None

    def save_plan(self, plan: TaskPlan) -> None:
        """Save the task plan."""
        self.ensure_state_dir()
        self._plan = plan
        self.task_plan_file.write_text(plan.to_markdown(), encoding="utf-8")

    def create_plan(self, goal: str, tasks: list[str] | None = None) -> TaskPlan:
        """Create a new task plan."""
        plan = TaskPlan(goal=goal)
        if tasks:
            for task in tasks:
                plan.add_task(task)
        self.save_plan(plan)
        return plan

    def clear_plan(self) -> bool:
        """Remove the current task plan."""
        if self.task_plan_file.exists():
            self.task_plan_file.unlink()
            self._plan = None
            return True
        return False

    def get_plan_context(self) -> str | None:
        """Get plan context for prompt injection. Returns None if no plan."""
        plan = self.load_plan()
        if plan and plan.tasks:
            return f"\n---\n**CURRENT TASK PLAN**:\n{plan.summary()}\n---\n"
        return None

    # Notes management
    def append_note(self, note: str) -> None:
        """Append a note to notes.md."""
        self.ensure_state_dir()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(self.notes_file, "a", encoding="utf-8") as f:
            f.write(f"\n## {timestamp}\n{note}\n")

    def get_notes(self) -> str | None:
        """Get contents of notes file."""
        if self.notes_file.exists():
            return self.notes_file.read_text(encoding="utf-8")
        return None

    def clear_notes(self) -> bool:
        """Clear notes file."""
        if self.notes_file.exists():
            self.notes_file.unlink()
            return True
        return False


# Tool implementations for the agent
def create_task_plan(goal: str, tasks: list[str], state_mgr: StateManager) -> dict[str, Any]:
    """Tool: Create a new task plan."""
    try:
        plan = state_mgr.create_plan(goal, tasks)
        return {
            "success": True,
            "message": f"Created plan with {len(tasks)} tasks",
            "plan": plan.summary()
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def update_task_status(task_index: int, status: str, state_mgr: StateManager) -> dict[str, Any]:
    """Tool: Update a task's status."""
    valid_statuses = {
        "pending": " ",
        "in_progress": "~",
        "done": "x",
        " ": " ",
        "~": "~",
        "x": "x"
    }

    if status not in valid_statuses:
        return {
            "success": False,
            "error": f"Invalid status '{status}'. Use: pending, in_progress, done"
        }

    plan = state_mgr.load_plan()
    if not plan:
        return {"success": False, "error": "No active task plan"}

    normalized_status = valid_statuses[status]
    if plan.update_task(task_index, normalized_status):
        state_mgr.save_plan(plan)
        return {
            "success": True,
            "message": f"Task {task_index} marked as {status}",
            "plan": plan.summary()
        }
    return {"success": False, "error": f"Task index {task_index} not found"}


def add_task(description: str, state_mgr: StateManager) -> dict[str, Any]:
    """Tool: Add a task to the current plan."""
    plan = state_mgr.load_plan()
    if not plan:
        return {"success": False, "error": "No active task plan. Create one first."}

    index = plan.add_task(description)
    state_mgr.save_plan(plan)
    return {
        "success": True,
        "message": f"Added task {index}: {description}",
        "plan": plan.summary()
    }


def get_plan_status(state_mgr: StateManager) -> dict[str, Any]:
    """Tool: Get current plan status."""
    plan = state_mgr.load_plan()
    if not plan:
        return {"success": True, "message": "No active task plan", "plan": None}
    return {"success": True, "plan": plan.summary()}


def clear_task_plan(state_mgr: StateManager) -> dict[str, Any]:
    """Tool: Clear the current task plan."""
    if state_mgr.clear_plan():
        return {"success": True, "message": "Task plan cleared"}
    return {"success": True, "message": "No task plan to clear"}
