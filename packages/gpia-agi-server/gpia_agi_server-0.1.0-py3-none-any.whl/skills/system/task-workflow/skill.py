"""
Task Workflow Skill - Autonomous Action Orchestrator
=====================================================

This skill transforms the cognitive system from passive to active.
It creates, manages, and executes task workflows autonomously
while maintaining full user control.

Architecture:
```
┌─────────────────────────────────────────────────────────────────┐
│                    WORKFLOW CONTROL PLANE                        │
│                                                                 │
│   USER CONTROLS                      AI AUTONOMY                │
│   ┌────────────┐                    ┌────────────┐             │
│   │ Create     │                    │ Execute    │             │
│   │ Pause      │ ◀──── BALANCE ────▶│ Adapt      │             │
│   │ Resume     │                    │ Complete   │             │
│   │ Cancel     │                    │ Learn      │             │
│   │ Modify     │                    │ Retry      │             │
│   └────────────┘                    └────────────┘             │
│                                                                 │
│   WORKFLOW STATES                                               │
│   ┌─────────────────────────────────────────────────┐          │
│   │ pending → running → completed                    │          │
│   │    ↓         ↓          ↓                        │          │
│   │ cancelled  paused    failed → retry              │          │
│   └─────────────────────────────────────────────────┘          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

Key Capabilities:
- create: Define a new workflow with tasks
- execute: Run a workflow (respects user controls)
- pause/resume/cancel: User control over execution
- adapt: Modify a running workflow
- autocomplete: AI suggests next steps
- status: Get workflow state
"""

from __future__ import annotations

import json
import logging
import sqlite3
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from skills.base import (
    Skill,
    SkillCategory,
    SkillContext,
    SkillLevel,
    SkillMetadata,
    SkillResult,
)

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"
    WAITING_USER = "waiting_user"  # Needs user input


class WorkflowStatus(str, Enum):
    DRAFT = "draft"
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """A single task in a workflow."""
    id: str
    name: str
    description: str
    skill_id: Optional[str] = None  # Skill to execute
    skill_input: Optional[Dict[str, Any]] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    requires_approval: bool = False  # User must approve before execution
    dependencies: List[str] = field(default_factory=list)  # Task IDs that must complete first
    retry_count: int = 0
    max_retries: int = 3

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "skill_id": self.skill_id,
            "skill_input": self.skill_input,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "requires_approval": self.requires_approval,
            "dependencies": self.dependencies,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
        }


@dataclass
class Workflow:
    """A workflow containing multiple tasks."""
    id: str
    name: str
    description: str
    tasks: List[Task] = field(default_factory=list)
    status: WorkflowStatus = WorkflowStatus.DRAFT
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    created_by: str = "system"  # "system" or "user"
    priority: int = 5  # 1=highest, 10=lowest
    schedule: Optional[str] = None  # Cron-like schedule for recurring
    context: Dict[str, Any] = field(default_factory=dict)  # Shared context

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "tasks": [t.to_dict() for t in self.tasks],
            "status": self.status.value,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "created_by": self.created_by,
            "priority": self.priority,
            "schedule": self.schedule,
            "context": self.context,
            "progress": self.progress,
        }

    @property
    def progress(self) -> Dict[str, int]:
        """Calculate workflow progress."""
        total = len(self.tasks)
        if total == 0:
            return {"total": 0, "completed": 0, "percent": 0}

        completed = sum(1 for t in self.tasks if t.status == TaskStatus.COMPLETED)
        return {
            "total": total,
            "completed": completed,
            "percent": int(completed / total * 100),
        }


class WorkflowStore:
    """Persistent storage for workflows."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Path("data/workflows.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS workflows (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    status TEXT NOT NULL,
                    priority INTEGER DEFAULT 5,
                    schedule TEXT,
                    data JSON NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_workflows_status
                ON workflows(status)
            """)

    def save(self, workflow: Workflow):
        """Save or update a workflow."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO workflows
                (id, name, description, status, priority, schedule, data, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                workflow.id,
                workflow.name,
                workflow.description,
                workflow.status.value,
                workflow.priority,
                workflow.schedule,
                json.dumps(workflow.to_dict()),
                workflow.created_at,
                datetime.now().isoformat(),
            ))

    def get(self, workflow_id: str) -> Optional[Workflow]:
        """Get a workflow by ID."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT data FROM workflows WHERE id = ?",
                (workflow_id,)
            ).fetchone()

            if row:
                return self._from_dict(json.loads(row[0]))
        return None

    def list(
        self,
        status: Optional[WorkflowStatus] = None,
        limit: int = 50,
    ) -> List[Workflow]:
        """List workflows, optionally filtered by status."""
        with sqlite3.connect(self.db_path) as conn:
            if status:
                rows = conn.execute(
                    "SELECT data FROM workflows WHERE status = ? ORDER BY priority, created_at DESC LIMIT ?",
                    (status.value, limit)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT data FROM workflows ORDER BY priority, created_at DESC LIMIT ?",
                    (limit,)
                ).fetchall()

            return [self._from_dict(json.loads(row[0])) for row in rows]

    def get_queued(self) -> List[Workflow]:
        """Get workflows ready to execute."""
        return self.list(status=WorkflowStatus.QUEUED)

    def delete(self, workflow_id: str):
        """Delete a workflow."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM workflows WHERE id = ?", (workflow_id,))

    def _from_dict(self, data: Dict[str, Any]) -> Workflow:
        """Reconstruct workflow from dict."""
        tasks = [
            Task(
                id=t["id"],
                name=t["name"],
                description=t["description"],
                skill_id=t.get("skill_id"),
                skill_input=t.get("skill_input"),
                status=TaskStatus(t["status"]),
                result=t.get("result"),
                error=t.get("error"),
                created_at=t.get("created_at", ""),
                started_at=t.get("started_at"),
                completed_at=t.get("completed_at"),
                requires_approval=t.get("requires_approval", False),
                dependencies=t.get("dependencies", []),
                retry_count=t.get("retry_count", 0),
                max_retries=t.get("max_retries", 3),
            )
            for t in data.get("tasks", [])
        ]

        return Workflow(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            tasks=tasks,
            status=WorkflowStatus(data["status"]),
            created_at=data.get("created_at", ""),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
            created_by=data.get("created_by", "system"),
            priority=data.get("priority", 5),
            schedule=data.get("schedule"),
            context=data.get("context", {}),
        )


class TaskWorkflowSkill(Skill):
    """
    Autonomous task workflow management.

    This skill enables the AI to:
    1. Create workflows from goals or user requests
    2. Execute tasks autonomously (within safety bounds)
    3. Respect user controls (pause, cancel, modify)
    4. Learn from execution outcomes
    5. Suggest autocomplete options
    """

    def __init__(self):
        self.store = WorkflowStore()
        self._memory = None
        self._mindset = None
        self._safety = None
        self._registry = None

    @property
    def memory(self):
        if self._memory is None:
            try:
                from skills.conscience.memory.skill import MemorySkill
                self._memory = MemorySkill()
            except Exception:
                pass
        return self._memory

    @property
    def mindset(self):
        if self._mindset is None:
            try:
                from skills.conscience.mindset.skill import MindsetSkill
                self._mindset = MindsetSkill()
            except Exception:
                pass
        return self._mindset

    @property
    def safety(self):
        if self._safety is None:
            try:
                from skills.conscience.safety.skill import SafetySkill
                self._safety = SafetySkill()
            except Exception:
                pass
        return self._safety

    @property
    def registry(self):
        if self._registry is None:
            try:
                from skills.registry import get_registry
                self._registry = get_registry()
            except Exception:
                pass
        return self._registry

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="system/task-workflow",
            name="Task Workflow",
            description="Autonomous task workflow creation and execution with user control",
            category=SkillCategory.AUTOMATION,
            level=SkillLevel.EXPERT,
            tags=["workflow", "automation", "tasks", "autonomous", "control"],
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "capability": {
                    "type": "string",
                    "enum": [
                        "create", "execute", "pause", "resume", "cancel",
                        "adapt", "autocomplete", "status", "list", "delete",
                        "approve", "reject", "retry",
                    ],
                },
                "workflow_id": {"type": "string"},
                "task_id": {"type": "string"},
                "goal": {"type": "string", "description": "Goal for workflow creation"},
                "tasks": {"type": "array", "description": "Task definitions"},
                "modifications": {"type": "object", "description": "Changes for adapt"},
            },
            "required": ["capability"],
        }

    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "workflow": {"type": "object"},
                "workflows": {"type": "array"},
                "suggestions": {"type": "array"},
            },
        }

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        capability = input_data.get("capability")

        handlers = {
            "create": self._create,
            "execute": self._execute,
            "pause": self._pause,
            "resume": self._resume,
            "cancel": self._cancel,
            "adapt": self._adapt,
            "autocomplete": self._autocomplete,
            "status": self._status,
            "list": self._list,
            "delete": self._delete,
            "approve": self._approve,
            "reject": self._reject,
            "retry": self._retry,
        }

        handler = handlers.get(capability)
        if not handler:
            return SkillResult(
                success=False,
                output=None,
                error=f"Unknown capability: {capability}",
                skill_id=self.metadata().id,
            )

        try:
            return handler(input_data, context)
        except Exception as e:
            logger.error(f"Workflow {capability} failed: {e}")
            return SkillResult(
                success=False,
                output=None,
                error=str(e),
                skill_id=self.metadata().id,
            )

    def _create(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """
        Create a workflow from a goal or task list.

        If given a goal, uses MindsetSkill to decompose into tasks.
        If given tasks, creates workflow directly.
        """
        goal = input_data.get("goal", "")
        tasks_input = input_data.get("tasks", [])
        name = input_data.get("name", "")

        workflow_id = str(uuid.uuid4())[:8]

        if goal and not tasks_input:
            # Use AI to decompose goal into tasks
            if self.mindset:
                decomposition = self.mindset.execute({
                    "capability": "think",
                    "problem": f"""
                    Decompose this goal into concrete tasks:

                    Goal: {goal}

                    For each task, specify:
                    1. Task name (short, action-oriented)
                    2. Task description (what exactly to do)
                    3. Required skill (if any from available skills)
                    4. Dependencies (which tasks must complete first)
                    5. Whether user approval is needed (for risky actions)

                    Output as a structured list.
                    """,
                    "pattern": "deep_analysis",
                    "store_reasoning": False,
                }, context)

                if decomposition.success:
                    # Parse AI output into tasks
                    tasks = self._parse_ai_tasks(
                        decomposition.output.get("conclusion", ""),
                        workflow_id,
                    )
                else:
                    return SkillResult(
                        success=False,
                        output=None,
                        error="Failed to decompose goal into tasks",
                        skill_id=self.metadata().id,
                    )
            else:
                return SkillResult(
                    success=False,
                    output=None,
                    error="MindsetSkill required for goal decomposition",
                    skill_id=self.metadata().id,
                )
        else:
            # Create tasks from input
            tasks = [
                Task(
                    id=f"{workflow_id}-{i}",
                    name=t.get("name", f"Task {i+1}"),
                    description=t.get("description", ""),
                    skill_id=t.get("skill_id"),
                    skill_input=t.get("skill_input"),
                    requires_approval=t.get("requires_approval", False),
                    dependencies=t.get("dependencies", []),
                )
                for i, t in enumerate(tasks_input)
            ]

        workflow = Workflow(
            id=workflow_id,
            name=name or f"Workflow for: {goal[:50] if goal else 'tasks'}",
            description=goal or "User-defined workflow",
            tasks=tasks,
            status=WorkflowStatus.DRAFT,
            created_by=context.user_id if hasattr(context, 'user_id') else "user",
        )

        self.store.save(workflow)

        return SkillResult(
            success=True,
            output={
                "workflow": workflow.to_dict(),
                "message": f"Workflow created with {len(tasks)} tasks",
            },
            skill_id=self.metadata().id,
        )

    def _parse_ai_tasks(self, ai_output: str, workflow_id: str) -> List[Task]:
        """Parse AI-generated task decomposition."""
        tasks = []
        lines = ai_output.split("\n")

        current_task = {}
        task_num = 0

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Simple heuristic parsing
            if line.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "-", "*")):
                if current_task.get("name"):
                    tasks.append(Task(
                        id=f"{workflow_id}-{task_num}",
                        name=current_task.get("name", f"Task {task_num + 1}"),
                        description=current_task.get("description", ""),
                        skill_id=current_task.get("skill_id"),
                        requires_approval=current_task.get("requires_approval", False),
                    ))
                    task_num += 1

                # Extract task name from line
                task_text = line.lstrip("0123456789.-* ")
                current_task = {"name": task_text[:100]}
            elif "description" in line.lower():
                current_task["description"] = line.split(":", 1)[-1].strip()
            elif "skill" in line.lower():
                current_task["skill_id"] = line.split(":", 1)[-1].strip()
            elif "approval" in line.lower() and "yes" in line.lower():
                current_task["requires_approval"] = True

        # Don't forget last task
        if current_task.get("name"):
            tasks.append(Task(
                id=f"{workflow_id}-{task_num}",
                name=current_task.get("name", f"Task {task_num + 1}"),
                description=current_task.get("description", ""),
                skill_id=current_task.get("skill_id"),
                requires_approval=current_task.get("requires_approval", False),
            ))

        return tasks

    def _execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """
        Execute a workflow or queue it for execution.

        Respects:
        - Task dependencies
        - User approval requirements
        - Safety constraints
        - Pause/cancel commands
        """
        workflow_id = input_data.get("workflow_id")
        if not workflow_id:
            return SkillResult(
                success=False,
                output=None,
                error="No workflow_id specified",
                skill_id=self.metadata().id,
            )

        workflow = self.store.get(workflow_id)
        if not workflow:
            return SkillResult(
                success=False,
                output=None,
                error=f"Workflow not found: {workflow_id}",
                skill_id=self.metadata().id,
            )

        # Queue for execution
        workflow.status = WorkflowStatus.QUEUED
        workflow.started_at = datetime.now().isoformat()
        self.store.save(workflow)

        # Execute tasks that are ready
        executed = []
        waiting = []

        for task in workflow.tasks:
            if task.status != TaskStatus.PENDING:
                continue

            # Check dependencies
            deps_met = all(
                any(t.id == dep and t.status == TaskStatus.COMPLETED for t in workflow.tasks)
                for dep in task.dependencies
            )

            if not deps_met:
                waiting.append(task.id)
                continue

            # Check if needs approval
            if task.requires_approval:
                task.status = TaskStatus.WAITING_USER
                waiting.append(task.id)
                continue

            # Execute task
            result = self._execute_task(task, workflow, context)
            executed.append({
                "task_id": task.id,
                "success": result.success,
                "result": result.output,
            })

        # Update workflow status
        self._update_workflow_status(workflow)
        self.store.save(workflow)

        return SkillResult(
            success=True,
            output={
                "workflow": workflow.to_dict(),
                "executed": executed,
                "waiting": waiting,
            },
            skill_id=self.metadata().id,
        )

    def _execute_task(
        self,
        task: Task,
        workflow: Workflow,
        context: SkillContext,
    ) -> SkillResult:
        """Execute a single task."""
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now().isoformat()

        try:
            # Check safety
            if self.safety and task.skill_id:
                safety_check = self.safety.execute({
                    "action_type": "skill_execution",
                    "target_path": task.skill_id,
                    "details": task.description,
                }, context)

                if not safety_check.output.get("allowed", True):
                    task.status = TaskStatus.WAITING_USER
                    task.error = f"Safety check: {safety_check.output.get('reason', 'Denied')}"
                    return SkillResult(success=False, output=None, error=task.error, skill_id=self.metadata().id)

            # Execute skill if specified
            if task.skill_id and self.registry:
                result = self.registry.execute_skill(
                    task.skill_id,
                    task.skill_input or {},
                    context,
                )

                if result.success:
                    task.status = TaskStatus.COMPLETED
                    task.result = result.output
                else:
                    task.status = TaskStatus.FAILED
                    task.error = result.error

                task.completed_at = datetime.now().isoformat()
                return result
            else:
                # No skill - mark as completed (manual task)
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now().isoformat()
                return SkillResult(success=True, output={"note": "Manual task completed"}, skill_id=self.metadata().id)

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now().isoformat()
            return SkillResult(success=False, output=None, error=str(e), skill_id=self.metadata().id)

    def _update_workflow_status(self, workflow: Workflow):
        """Update workflow status based on task states."""
        statuses = [t.status for t in workflow.tasks]

        if all(s == TaskStatus.COMPLETED for s in statuses):
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.now().isoformat()
        elif any(s == TaskStatus.FAILED for s in statuses):
            workflow.status = WorkflowStatus.FAILED
        elif any(s == TaskStatus.RUNNING for s in statuses):
            workflow.status = WorkflowStatus.RUNNING
        elif any(s == TaskStatus.WAITING_USER for s in statuses):
            workflow.status = WorkflowStatus.PAUSED

    def _pause(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Pause a running workflow."""
        workflow_id = input_data.get("workflow_id")
        workflow = self.store.get(workflow_id)

        if not workflow:
            return SkillResult(success=False, output=None, error="Workflow not found", skill_id=self.metadata().id)

        workflow.status = WorkflowStatus.PAUSED
        self.store.save(workflow)

        return SkillResult(
            success=True,
            output={"workflow": workflow.to_dict(), "message": "Workflow paused"},
            skill_id=self.metadata().id,
        )

    def _resume(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Resume a paused workflow."""
        workflow_id = input_data.get("workflow_id")
        workflow = self.store.get(workflow_id)

        if not workflow:
            return SkillResult(success=False, output=None, error="Workflow not found", skill_id=self.metadata().id)

        workflow.status = WorkflowStatus.QUEUED
        self.store.save(workflow)

        # Continue execution
        return self._execute({"workflow_id": workflow_id}, context)

    def _cancel(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Cancel a workflow."""
        workflow_id = input_data.get("workflow_id")
        workflow = self.store.get(workflow_id)

        if not workflow:
            return SkillResult(success=False, output=None, error="Workflow not found", skill_id=self.metadata().id)

        workflow.status = WorkflowStatus.CANCELLED
        for task in workflow.tasks:
            if task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
                task.status = TaskStatus.CANCELLED

        self.store.save(workflow)

        return SkillResult(
            success=True,
            output={"workflow": workflow.to_dict(), "message": "Workflow cancelled"},
            skill_id=self.metadata().id,
        )

    def _adapt(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Modify a workflow (add/remove/change tasks)."""
        workflow_id = input_data.get("workflow_id")
        modifications = input_data.get("modifications", {})

        workflow = self.store.get(workflow_id)
        if not workflow:
            return SkillResult(success=False, output=None, error="Workflow not found", skill_id=self.metadata().id)

        # Apply modifications
        if "add_tasks" in modifications:
            for t in modifications["add_tasks"]:
                new_task = Task(
                    id=f"{workflow_id}-{len(workflow.tasks)}",
                    name=t.get("name", "New Task"),
                    description=t.get("description", ""),
                    skill_id=t.get("skill_id"),
                    requires_approval=t.get("requires_approval", False),
                )
                workflow.tasks.append(new_task)

        if "remove_tasks" in modifications:
            workflow.tasks = [t for t in workflow.tasks if t.id not in modifications["remove_tasks"]]

        if "update_task" in modifications:
            for task in workflow.tasks:
                if task.id == modifications["update_task"].get("id"):
                    if "name" in modifications["update_task"]:
                        task.name = modifications["update_task"]["name"]
                    if "description" in modifications["update_task"]:
                        task.description = modifications["update_task"]["description"]

        self.store.save(workflow)

        return SkillResult(
            success=True,
            output={"workflow": workflow.to_dict(), "message": "Workflow adapted"},
            skill_id=self.metadata().id,
        )

    def _autocomplete(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Suggest next steps or completions for a workflow."""
        workflow_id = input_data.get("workflow_id")
        workflow = self.store.get(workflow_id)

        if not workflow:
            return SkillResult(success=False, output=None, error="Workflow not found", skill_id=self.metadata().id)

        suggestions = []

        # Find pending tasks
        pending = [t for t in workflow.tasks if t.status == TaskStatus.PENDING]
        failed = [t for t in workflow.tasks if t.status == TaskStatus.FAILED]
        waiting = [t for t in workflow.tasks if t.status == TaskStatus.WAITING_USER]

        if waiting:
            suggestions.append({
                "action": "approve",
                "description": f"{len(waiting)} tasks waiting for approval",
                "task_ids": [t.id for t in waiting],
            })

        if failed:
            suggestions.append({
                "action": "retry",
                "description": f"{len(failed)} tasks failed - retry available",
                "task_ids": [t.id for t in failed if t.retry_count < t.max_retries],
            })

        if pending:
            suggestions.append({
                "action": "execute",
                "description": f"{len(pending)} tasks ready to execute",
            })

        # Use AI for smarter suggestions
        if self.mindset and workflow.status in [WorkflowStatus.PAUSED, WorkflowStatus.FAILED]:
            analysis = self.mindset.execute({
                "capability": "analyze",
                "problem": f"""
                Workflow "{workflow.name}" is {workflow.status.value}.

                Current state:
                - Completed: {sum(1 for t in workflow.tasks if t.status == TaskStatus.COMPLETED)}
                - Failed: {len(failed)}
                - Waiting: {len(waiting)}

                What should be done next?
                """,
                "pattern": "rapid_iteration",
                "store_reasoning": False,
            }, context)

            if analysis.success:
                suggestions.append({
                    "action": "ai_recommendation",
                    "description": analysis.output.get("conclusion", "")[:200],
                })

        return SkillResult(
            success=True,
            output={
                "workflow": workflow.to_dict(),
                "suggestions": suggestions,
            },
            skill_id=self.metadata().id,
        )

    def _approve(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Approve a task waiting for user approval."""
        workflow_id = input_data.get("workflow_id")
        task_id = input_data.get("task_id")

        workflow = self.store.get(workflow_id)
        if not workflow:
            return SkillResult(success=False, output=None, error="Workflow not found", skill_id=self.metadata().id)

        for task in workflow.tasks:
            if task.id == task_id and task.status == TaskStatus.WAITING_USER:
                task.status = TaskStatus.PENDING
                task.requires_approval = False  # Already approved
                break

        self.store.save(workflow)

        # Continue execution
        return self._execute({"workflow_id": workflow_id}, context)

    def _reject(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Reject a task waiting for approval."""
        workflow_id = input_data.get("workflow_id")
        task_id = input_data.get("task_id")

        workflow = self.store.get(workflow_id)
        if not workflow:
            return SkillResult(success=False, output=None, error="Workflow not found", skill_id=self.metadata().id)

        for task in workflow.tasks:
            if task.id == task_id:
                task.status = TaskStatus.CANCELLED
                break

        self.store.save(workflow)

        return SkillResult(
            success=True,
            output={"workflow": workflow.to_dict(), "message": f"Task {task_id} rejected"},
            skill_id=self.metadata().id,
        )

    def _retry(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Retry a failed task."""
        workflow_id = input_data.get("workflow_id")
        task_id = input_data.get("task_id")

        workflow = self.store.get(workflow_id)
        if not workflow:
            return SkillResult(success=False, output=None, error="Workflow not found", skill_id=self.metadata().id)

        for task in workflow.tasks:
            if task.id == task_id and task.status == TaskStatus.FAILED:
                if task.retry_count < task.max_retries:
                    task.status = TaskStatus.PENDING
                    task.retry_count += 1
                    task.error = None
                else:
                    return SkillResult(
                        success=False,
                        output=None,
                        error=f"Max retries ({task.max_retries}) exceeded",
                        skill_id=self.metadata().id,
                    )

        self.store.save(workflow)

        # Continue execution
        return self._execute({"workflow_id": workflow_id}, context)

    def _status(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Get workflow status."""
        workflow_id = input_data.get("workflow_id")
        workflow = self.store.get(workflow_id)

        if not workflow:
            return SkillResult(success=False, output=None, error="Workflow not found", skill_id=self.metadata().id)

        return SkillResult(
            success=True,
            output={"workflow": workflow.to_dict()},
            skill_id=self.metadata().id,
        )

    def _list(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """List all workflows."""
        status_filter = input_data.get("status")
        status = WorkflowStatus(status_filter) if status_filter else None

        workflows = self.store.list(status=status)

        return SkillResult(
            success=True,
            output={
                "workflows": [w.to_dict() for w in workflows],
                "count": len(workflows),
            },
            skill_id=self.metadata().id,
        )

    def _delete(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Delete a workflow."""
        workflow_id = input_data.get("workflow_id")
        self.store.delete(workflow_id)

        return SkillResult(
            success=True,
            output={"message": f"Workflow {workflow_id} deleted"},
            skill_id=self.metadata().id,
        )


__all__ = ["TaskWorkflowSkill", "Workflow", "Task", "WorkflowStatus", "TaskStatus"]
