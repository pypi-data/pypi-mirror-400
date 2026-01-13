"""Blueprint data models (Pydantic V2).

Defines the core data structures for Blueprint Standard Format v1.3.0.
Uses Pydantic for robust validation of LLM-generated outputs.

v1.3.0 Changes:
- Added ExecutionContext sub-model for agent execution environment
- Added ErrorPolicy sub-model for failure handling
- Enhanced Interface with typed schema support
- All new fields are optional for backward compatibility

Migration from dataclasses to Pydantic V2 provides:
- Automatic type coercion (string "2" → int 2)
- Graceful handling of missing optional fields
- Better error messages for invalid inputs
- Serialization/deserialization built-in
"""
from datetime import date
from enum import Enum
from typing import Optional, Any

from pydantic import BaseModel, Field, field_validator, model_validator


# =============================================================================
# ENUMS
# =============================================================================

class TaskStatus(str, Enum):
    """Task execution status."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    BLOCKED = "blocked"
    SKIPPED = "skipped"


class TierStatus(str, Enum):
    """Tier execution status."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    BLOCKED = "blocked"


class NotificationChannel(str, Enum):
    """Notification delivery channel."""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    ENV = "env"
    CONSOLE = "console"


class TimeoutAction(str, Enum):
    """Action to take on timeout or missing value."""
    ABORT = "abort"
    SKIP = "skip"
    CONTINUE = "continue"


class FailureAction(str, Enum):
    """Action to take when task fails (v1.3.0)."""
    BLOCK = "block"      # Mark task blocked, continue other independent tasks
    ABORT = "abort"      # Stop entire Blueprint execution
    SKIP = "skip"        # Mark task skipped, proceed to dependents


# =============================================================================
# v1.3.0 SUB-MODELS
# =============================================================================

class ErrorPolicy(BaseModel):
    """Error handling policy for task failures (v1.3.0).
    
    Defines what happens when test_command fails.
    
    Example:
        on_failure:
          max_retries: 2
          retry_delay_seconds: 10
          action: block
    """
    max_retries: int = Field(default=0, ge=0, description="Number of retry attempts")
    retry_delay_seconds: int = Field(default=5, ge=0, description="Delay between retries")
    action: FailureAction = Field(default=FailureAction.BLOCK, description="Action after all retries exhausted")
    
    model_config = {"extra": "ignore"}
    
    @field_validator("action", mode="before")
    @classmethod
    def parse_action(cls, v):
        """Handle string action values."""
        if isinstance(v, str):
            return v.lower()
        return v


class ExecutionContext(BaseModel):
    """Execution environment for task commands (v1.3.0).
    
    Tells AI agents HOW to execute the task.
    
    Example:
        execution_context:
          working_directory: "/project/src"
          environment_variables:
            PYTHONPATH: "/project/src"
            JWT_SECRET: "${secrets.JWT_SECRET}"
          required_tools: [python3, pytest]
          timeout_seconds: 300
          setup_command: "pip install -r requirements.txt"
    """
    working_directory: Optional[str] = Field(
        default=None, 
        description="Absolute path for command execution"
    )
    environment_variables: dict[str, str] = Field(
        default_factory=dict,
        description="Env vars required for execution. Use ${secrets.NAME} for secret refs."
    )
    required_tools: list[str] = Field(
        default_factory=list,
        description="Tools that must be available (e.g., python3, npm, docker)"
    )
    timeout_seconds: int = Field(
        default=3600,
        ge=1,
        description="Max execution time in seconds"
    )
    setup_command: Optional[str] = Field(
        default=None,
        description="Command to run before test_command (install deps, etc.)"
    )
    
    model_config = {"extra": "ignore"}


class Interface(BaseModel):
    """Task input/output contract with optional typed schema (v1.3.0).
    
    Basic usage (required):
        interface:
          input: "User credentials"
          output: "JWT token"
    
    Typed usage (recommended for autonomous execution):
        interface:
          input: "User credentials"
          input_type: json
          input_schema:
            type: object
            properties:
              user_id: { type: string }
            required: [user_id]
          example_input: '{"user_id": "u123"}'
          output: "JWT token"
          output_type: json
          output_schema:
            type: object
            properties:
              token: { type: string }
          example_output: '{"token": "eyJ..."}'
    """
    # Required fields (v0.1.0)
    input: str = Field(description="Human-readable description of required input")
    output: str = Field(description="Human-readable description of produced output")
    
    # Optional typed fields (v1.3.0)
    input_type: Optional[str] = Field(
        default=None,
        description="Input data type: json | yaml | text | file_path | none"
    )
    output_type: Optional[str] = Field(
        default=None,
        description="Output data type: json | yaml | text | file_path | none"
    )
    input_schema: Optional[dict[str, Any]] = Field(
        default=None,
        description="JSON Schema for input validation"
    )
    output_schema: Optional[dict[str, Any]] = Field(
        default=None,
        description="JSON Schema for output validation"
    )
    example_input: Optional[str] = Field(
        default=None,
        description="Concrete example input (JSON string or value)"
    )
    example_output: Optional[str] = Field(
        default=None,
        description="Concrete example output (JSON string or value)"
    )
    
    model_config = {"extra": "ignore"}
    
    def has_schema(self) -> bool:
        """Check if typed schema is defined."""
        return self.input_schema is not None or self.output_schema is not None
    
    def has_examples(self) -> bool:
        """Check if examples are provided."""
        return self.example_input is not None or self.example_output is not None


# =============================================================================
# HUMAN-IN-THE-LOOP
# =============================================================================

class Notification(BaseModel):
    """Notification configuration for HUMAN_REQUIRED blocks."""
    channel: NotificationChannel
    recipient: Optional[str] = None
    variable: Optional[str] = None
    variables: list[str] = Field(default_factory=list)
    url: Optional[str] = None
    webhook: Optional[str] = None
    
    model_config = {"extra": "ignore"}


class HumanRequired(BaseModel):
    """Human-in-the-loop signal block."""
    action: str
    reason: str
    notify: Notification
    timeout: Optional[str] = None
    on_timeout: TimeoutAction = TimeoutAction.ABORT
    on_missing: TimeoutAction = TimeoutAction.ABORT
    
    model_config = {"extra": "ignore"}
    
    @field_validator("on_timeout", "on_missing", mode="before")
    @classmethod
    def parse_timeout_action(cls, v):
        """Handle 'ABORT with instructions' style strings from LLM."""
        if isinstance(v, str):
            v_lower = v.lower().split()[0]  # Take first word
            if v_lower in ("abort", "skip", "continue"):
                return v_lower
        return v


# =============================================================================
# TASK MODEL
# =============================================================================

class Task(BaseModel):
    """A single task in a Blueprint.
    
    v1.3.0 adds optional nested fields for:
    - execution_context: How to execute (working dir, env, tools)
    - on_failure: Error handling policy
    - Enhanced interface with typed schemas
    
    All v1.3.0 fields are optional for backward compatibility.
    """
    # Core fields (v0.1.0)
    task_id: str
    name: str
    status: TaskStatus = TaskStatus.NOT_STARTED
    dependencies: list[str] = Field(default_factory=list)
    interface: Optional[Interface] = None
    acceptance_criteria: list[str] = Field(default_factory=list)
    test_command: str = ""
    rollback: str = ""
    
    # Optional core fields (v0.1.0)
    assignee: Optional[str] = None
    estimated_sessions: Optional[int] = None
    files_to_create: list[str] = Field(default_factory=list)
    files_to_modify: list[str] = Field(default_factory=list)
    human_required: Optional[HumanRequired] = None
    notes: Optional[str] = None
    example: Optional[dict] = None
    
    # v1.3.0 nested fields
    execution_context: Optional[ExecutionContext] = Field(
        default=None,
        description="Execution environment for agent (v1.3.0)"
    )
    on_failure: Optional[ErrorPolicy] = Field(
        default=None,
        description="Error handling policy (v1.3.0)"
    )
    on_success: Optional[str] = Field(
        default=None,
        description="Command to run after successful execution (v1.3.0)"
    )
    
    model_config = {"extra": "ignore"}
    
    @field_validator("status", mode="before")
    @classmethod
    def parse_status(cls, v):
        """Handle emoji status markers from markdown."""
        if isinstance(v, str):
            emoji_map = {
                "🔲": "not_started",
                "🔄": "in_progress", 
                "✅": "complete",
                "⛔": "blocked",
                "⏭️": "skipped",
            }
            # Check if starts with emoji
            for emoji, status in emoji_map.items():
                if v.startswith(emoji):
                    return status
            # Already lowercase status
            return v.lower().replace(" ", "_")
        return v
    
    @field_validator("estimated_sessions", mode="before")
    @classmethod
    def coerce_sessions(cls, v):
        """Coerce string to int for estimated_sessions."""
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                return None
        return v
    
    def is_blocked(self) -> bool:
        """Check if task is blocked by dependencies or human requirement."""
        return self.status == TaskStatus.BLOCKED
    
    def requires_human(self) -> bool:
        """Check if task requires human intervention."""
        return self.human_required is not None
    
    def has_execution_context(self) -> bool:
        """Check if task has execution context defined (v1.3.0)."""
        return self.execution_context is not None
    
    def has_error_policy(self) -> bool:
        """Check if task has error policy defined (v1.3.0)."""
        return self.on_failure is not None
    
    def has_typed_interface(self) -> bool:
        """Check if task has typed interface schema (v1.3.0)."""
        return self.interface is not None and self.interface.has_schema()
    
    def get_effective_timeout(self) -> int:
        """Get timeout in seconds (from execution_context or default)."""
        if self.execution_context and self.execution_context.timeout_seconds:
            return self.execution_context.timeout_seconds
        return 3600  # Default 1 hour
    
    def get_effective_retries(self) -> int:
        """Get max retries (from on_failure or default 0)."""
        if self.on_failure:
            return self.on_failure.max_retries
        return 0


# =============================================================================
# TIER AND DOCUMENT MODELS (unchanged from v0.1.0)
# =============================================================================

class Tier(BaseModel):
    """A tier (phase) in a Blueprint."""
    tier_id: str
    name: str
    tasks: list[Task] = Field(default_factory=list)
    goal: Optional[str] = None
    status: TierStatus = TierStatus.NOT_STARTED
    
    model_config = {"extra": "ignore"}
    
    def task_count(self) -> int:
        """Get total number of tasks in tier."""
        return len(self.tasks)
    
    def completed_count(self) -> int:
        """Get number of completed tasks."""
        return sum(1 for t in self.tasks if t.status == TaskStatus.COMPLETE)
    
    @model_validator(mode="after")
    def compute_status(self):
        """Auto-compute tier status from tasks."""
        if not self.tasks:
            return self
        completed = self.completed_count()
        total = self.task_count()
        if completed == total:
            self.status = TierStatus.COMPLETE
        elif completed > 0:
            self.status = TierStatus.IN_PROGRESS
        elif any(t.status == TaskStatus.BLOCKED for t in self.tasks):
            self.status = TierStatus.BLOCKED
        return self


class SuccessMetric(BaseModel):
    """A success metric for the Blueprint."""
    metric: str
    target: str
    validation: Optional[str] = None
    
    model_config = {"extra": "ignore"}


class Metadata(BaseModel):
    """Blueprint document metadata."""
    title: str
    status: str = "draft"
    owner: str = "Unknown"
    description: Optional[str] = None
    created: Optional[date] = None
    updated: Optional[date] = None
    repository: Optional[str] = None
    
    model_config = {"extra": "ignore"}
    
    @field_validator("created", "updated", mode="before")
    @classmethod
    def parse_date(cls, v):
        """Parse date from string."""
        if isinstance(v, str):
            try:
                return date.fromisoformat(v)
            except ValueError:
                return None
        return v


class DependencyEdge(BaseModel):
    """An edge in the dependency graph."""
    from_task: str
    to_task: str


class ParallelGroup(BaseModel):
    """A group of tasks that can run in parallel."""
    group_id: str
    tasks: list[str]
    description: Optional[str] = None


class DependencyGraph(BaseModel):
    """Dependency graph structure."""
    nodes: list[str] = Field(default_factory=list)
    edges: list[DependencyEdge] = Field(default_factory=list)
    parallelizable_groups: list[ParallelGroup] = Field(default_factory=list)


class VersionHistoryEntry(BaseModel):
    """A single entry in document version history."""
    version: str
    date: date
    author: str
    changes: str
    
    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, v):
        """Parse date from string."""
        if isinstance(v, str):
            try:
                return date.fromisoformat(v)
            except ValueError:
                return date.today()
        return v


class DocumentControl(BaseModel):
    """Document version control information."""
    version: str = "1.3.0"
    history: list[VersionHistoryEntry] = Field(default_factory=list)


class BlueprintRef(BaseModel):
    """Reference to another Blueprint (Linker support).
    
    Enables hierarchical compilation by allowing Blueprints to reference
    sub-modules. This prevents context window overflow for large projects.
    """
    ref: str  # Path to referenced Blueprint (e.g., "./auth-module.bp.md")
    required: bool = True  # If false, missing ref is warning not error
    inline: bool = False  # If true, inline tasks; if false, treat as dependency


class Blueprint(BaseModel):
    """A complete Blueprint specification.
    
    This is the top-level container that holds all components of a Blueprint
    document. It can be serialized to/from JSON and Markdown formats.
    
    Supports hierarchical compilation via `refs` field for large projects.
    
    v1.3.0: Tasks may now include execution_context, on_failure, and typed interfaces.
    """
    blueprint_version: str = "1.3.0"
    metadata: Metadata
    tiers: list[Tier] = Field(default_factory=list)
    strategic_vision: Optional[str] = None
    success_metrics: list[SuccessMetric] = Field(default_factory=list)
    dependency_graph: Optional[DependencyGraph] = None
    document_control: Optional[DocumentControl] = None
    refs: list[BlueprintRef] = Field(default_factory=list)
    
    model_config = {"extra": "ignore"}
    
    def all_tasks(self) -> list[Task]:
        """Get all tasks across all tiers."""
        return [task for tier in self.tiers for task in tier.tasks]
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        for task in self.all_tasks():
            if task.task_id == task_id:
                return task
        return None
    
    def total_tasks(self) -> int:
        """Get total number of tasks."""
        return len(self.all_tasks())
    
    def completed_tasks(self) -> int:
        """Get number of completed tasks."""
        return sum(1 for t in self.all_tasks() if t.status == TaskStatus.COMPLETE)
    
    def progress_percent(self) -> float:
        """Get completion percentage."""
        total = self.total_tasks()
        if total == 0:
            return 0.0
        return (self.completed_tasks() / total) * 100
    
    def has_refs(self) -> bool:
        """Check if Blueprint references other modules."""
        return len(self.refs) > 0
    
    def human_required_tasks(self) -> list[Task]:
        """Get all tasks requiring human intervention."""
        return [t for t in self.all_tasks() if t.requires_human()]
    
    def tasks_with_execution_context(self) -> list[Task]:
        """Get all tasks with execution context defined (v1.3.0)."""
        return [t for t in self.all_tasks() if t.has_execution_context()]
    
    def tasks_with_typed_interface(self) -> list[Task]:
        """Get all tasks with typed interface schema (v1.3.0)."""
        return [t for t in self.all_tasks() if t.has_typed_interface()]
