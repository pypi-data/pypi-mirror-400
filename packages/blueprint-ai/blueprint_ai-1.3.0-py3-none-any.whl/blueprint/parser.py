"""Blueprint parser - reads Blueprint markdown files into structured objects.

The parser handles both Markdown format (with embedded YAML blocks) and
pure JSON format Blueprints.

v1.3.0: Added support for execution_context, on_failure, and typed interfaces.
"""
import re
import json
import yaml
from pathlib import Path
from datetime import date
from typing import Union, Optional

from blueprint.models import (
    Blueprint,
    Task,
    Tier,
    TaskStatus,
    TierStatus,
    Interface,
    ExecutionContext,
    ErrorPolicy,
    FailureAction,
    HumanRequired,
    Notification,
    NotificationChannel,
    TimeoutAction,
    SuccessMetric,
    Metadata,
    DependencyGraph,
    DependencyEdge,
    ParallelGroup,
    DocumentControl,
    VersionHistoryEntry,
)


class ParseError(Exception):
    """Raised when Blueprint parsing fails."""
    def __init__(self, message: str, line: Optional[int] = None, context: Optional[str] = None):
        self.message = message
        self.line = line
        self.context = context
        super().__init__(self._format_message())
    
    def _format_message(self) -> str:
        msg = self.message
        if self.line:
            msg = f"Line {self.line}: {msg}"
        if self.context:
            msg = msg + "\n  Context: " + self.context
        return msg


def parse_file(filepath: Union[str, Path]) -> Blueprint:
    """Parse a Blueprint from a file."""
    path = Path(filepath)
    content = path.read_text(encoding="utf-8")
    
    if path.suffix == ".json":
        return parse_json(content)
    else:
        return parse_markdown(content)


def parse_json(content: str) -> Blueprint:
    """Parse a Blueprint from JSON string."""
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise ParseError(f"Invalid JSON: {e.msg}", line=e.lineno)
    
    return _parse_dict(data)


def parse_markdown(content: str) -> Blueprint:
    """Parse a Blueprint from Markdown string."""
    metadata = _extract_metadata(content)
    vision = _extract_section(content, "Strategic Vision")
    metrics = _extract_success_metrics(content)
    tasks_by_tier = _extract_task_blocks(content)
    
    tiers = []
    for tier_id, tier_data in tasks_by_tier.items():
        tier = Tier(
            tier_id=tier_id,
            name=tier_data.get("name", tier_id),
            goal=tier_data.get("goal"),
            tasks=tier_data.get("tasks", []),
            status=TierStatus.NOT_STARTED,
        )
        if all(t.status == TaskStatus.COMPLETE for t in tier.tasks):
            tier.status = TierStatus.COMPLETE
        elif any(t.status in (TaskStatus.IN_PROGRESS, TaskStatus.COMPLETE) for t in tier.tasks):
            tier.status = TierStatus.IN_PROGRESS
        tiers.append(tier)
    
    dep_graph = _build_dependency_graph(tiers)
    
    return Blueprint(
        blueprint_version="1.3.0",
        metadata=metadata,
        tiers=tiers,
        strategic_vision=vision,
        success_metrics=metrics,
        dependency_graph=dep_graph,
    )


def _extract_metadata(content: str) -> Metadata:
    """Extract document metadata from header."""
    title_match = re.search(r"^#\s+(.+?)(?:\s*—|\s*$)", content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "Untitled Blueprint"
    
    owner_match = re.search(r"\*\*Owner\*\*:\s*(.+?)$", content, re.MULTILINE)
    owner = owner_match.group(1).strip() if owner_match else "Unknown"
    
    status_match = re.search(r"\*\*Document Status\*\*:\s*(.+?)$", content, re.MULTILINE)
    status = status_match.group(1).strip().lower() if status_match else "draft"
    
    updated_match = re.search(r"\*\*Last Updated\*\*:\s*(\d{4}-\d{2}-\d{2})", content)
    updated = None
    if updated_match:
        try:
            updated = date.fromisoformat(updated_match.group(1))
        except ValueError:
            pass
    
    return Metadata(
        title=title,
        status=status,
        owner=owner,
        updated=updated,
    )


def _extract_section(content: str, section_name: str) -> Optional[str]:
    """Extract content of a named section."""
    pattern = r"##\s+" + re.escape(section_name) + r"\s*\n+(.*?)(?=\n##|\n---|\Z)"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        text = match.group(1).strip()
        text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
        return text
    return None


def _extract_success_metrics(content: str) -> list[SuccessMetric]:
    """Extract success metrics table."""
    metrics = []
    section = _extract_section(content, "Success Metrics")
    if not section:
        return metrics
    
    rows = re.findall(r"\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]*)\s*\|", section)
    for row in rows:
        if row[0].strip().lower() == "metric" or row[0].strip().startswith("-"):
            continue
        metrics.append(SuccessMetric(
            metric=row[0].strip(),
            target=row[1].strip(),
            validation=row[2].strip() if row[2].strip() else None,
        ))
    
    return metrics


def _extract_task_blocks(content: str) -> dict:
    """Extract all task YAML blocks from markdown."""
    tiers = {}
    
    tier_pattern = r"##\s+Tier\s+(\d+):\s*(.+?)(?=\n##|\Z)"
    tier_matches = re.finditer(tier_pattern, content, re.DOTALL)
    
    for tier_match in tier_matches:
        tier_num = tier_match.group(1)
        tier_id = f"T{tier_num}"
        tier_content = tier_match.group(2)
        
        tier_name_match = re.match(r"([^\n]+)", tier_content)
        tier_name = tier_name_match.group(1).strip() if tier_name_match else f"Tier {tier_num}"
        
        yaml_pattern = r"```yaml\s*\n(.*?)```"
        yaml_blocks = re.findall(yaml_pattern, tier_content, re.DOTALL)
        
        tasks = []
        for yaml_content in yaml_blocks:
            try:
                task_data = yaml.safe_load(yaml_content)
                if task_data and "task_id" in task_data:
                    tasks.append(_parse_task(task_data))
            except yaml.YAMLError:
                continue
        
        tiers[tier_id] = {
            "name": tier_name,
            "tasks": tasks,
        }
    
    return tiers


def _parse_timeout_action(value: str) -> TimeoutAction:
    """Parse timeout action, tolerant of extra text."""
    if not value:
        return TimeoutAction.ABORT
    value_lower = str(value).lower()
    if value_lower.startswith("abort"):
        return TimeoutAction.ABORT
    elif value_lower.startswith("skip"):
        return TimeoutAction.SKIP
    elif value_lower.startswith("continue"):
        return TimeoutAction.CONTINUE
    return TimeoutAction.ABORT


def _parse_failure_action(value: str) -> FailureAction:
    """Parse failure action for on_failure block (v1.3.0)."""
    if not value:
        return FailureAction.BLOCK
    value_lower = str(value).lower()
    if value_lower.startswith("abort"):
        return FailureAction.ABORT
    elif value_lower.startswith("skip"):
        return FailureAction.SKIP
    elif value_lower.startswith("block"):
        return FailureAction.BLOCK
    return FailureAction.BLOCK


def _parse_interface(data: dict) -> Optional[Interface]:
    """Parse interface block with v1.3.0 typed schema support."""
    if not data:
        return None
    
    return Interface(
        # Required fields (v0.1.0)
        input=data.get("input", ""),
        output=data.get("output", ""),
        # Optional typed fields (v1.3.0)
        input_type=data.get("input_type"),
        output_type=data.get("output_type"),
        input_schema=data.get("input_schema"),
        output_schema=data.get("output_schema"),
        example_input=data.get("example_input"),
        example_output=data.get("example_output"),
    )


def _parse_execution_context(data: dict) -> Optional[ExecutionContext]:
    """Parse execution_context block (v1.3.0)."""
    if not data:
        return None
    
    return ExecutionContext(
        working_directory=data.get("working_directory"),
        environment_variables=data.get("environment_variables", {}),
        required_tools=data.get("required_tools", []),
        timeout_seconds=data.get("timeout_seconds", 3600),
        setup_command=data.get("setup_command"),
    )


def _parse_error_policy(data: dict) -> Optional[ErrorPolicy]:
    """Parse on_failure block (v1.3.0)."""
    if not data:
        return None
    
    return ErrorPolicy(
        max_retries=data.get("max_retries", 0),
        retry_delay_seconds=data.get("retry_delay_seconds", 5),
        action=_parse_failure_action(data.get("action", "block")),
    )


def _parse_task(data: dict) -> Task:
    """Parse a task dictionary into a Task object.
    
    Supports both v0.1.0 and v1.3.0 task formats.
    """
    # Parse status with emoji support
    status_str = data.get("status", "not_started")
    status_map = {
        "🔲": TaskStatus.NOT_STARTED,
        "🔄": TaskStatus.IN_PROGRESS,
        "✅": TaskStatus.COMPLETE,
        "⛔": TaskStatus.BLOCKED,
        "⏭️": TaskStatus.SKIPPED,
        "not_started": TaskStatus.NOT_STARTED,
        "in_progress": TaskStatus.IN_PROGRESS,
        "complete": TaskStatus.COMPLETE,
        "blocked": TaskStatus.BLOCKED,
        "skipped": TaskStatus.SKIPPED,
    }
    status = TaskStatus.NOT_STARTED
    for key, value in status_map.items():
        if key in str(status_str):
            status = value
            break
    
    # Parse interface with v1.3.0 typed schema support
    interface = _parse_interface(data.get("interface", {}))
    
    # Parse human_required block
    human_required = None
    hr_data = data.get("human_required")
    if hr_data:
        notify_data = hr_data.get("notify", {})
        notify = Notification(
            channel=NotificationChannel(notify_data.get("channel", "console")),
            recipient=notify_data.get("recipient"),
            variable=notify_data.get("variable"),
            variables=notify_data.get("variables", []),
            url=notify_data.get("url"),
            webhook=notify_data.get("webhook"),
        )
        human_required = HumanRequired(
            action=hr_data.get("action", ""),
            reason=hr_data.get("reason", ""),
            notify=notify,
            timeout=hr_data.get("timeout"),
            on_timeout=_parse_timeout_action(hr_data.get("on_timeout", "abort")),
            on_missing=_parse_timeout_action(hr_data.get("on_missing", "abort")),
        )
    
    # Parse v1.3.0 nested blocks
    execution_context = _parse_execution_context(data.get("execution_context"))
    on_failure = _parse_error_policy(data.get("on_failure"))
    
    return Task(
        # Core fields (v0.1.0)
        task_id=data.get("task_id", ""),
        name=data.get("name", ""),
        status=status,
        dependencies=data.get("dependencies", []),
        interface=interface,
        acceptance_criteria=data.get("acceptance_criteria", []),
        test_command=data.get("test_command", ""),
        rollback=data.get("rollback", ""),
        # Optional core fields (v0.1.0)
        assignee=data.get("assignee"),
        estimated_sessions=data.get("estimated_sessions"),
        files_to_create=data.get("files_to_create", []),
        files_to_modify=data.get("files_to_modify", []),
        human_required=human_required,
        notes=data.get("notes"),
        example=data.get("example"),
        # v1.3.0 nested fields
        execution_context=execution_context,
        on_failure=on_failure,
        on_success=data.get("on_success"),
    )


def _parse_dict(data: dict) -> Blueprint:
    """Parse a Blueprint from a dictionary (JSON format)."""
    meta_data = data.get("metadata", {})
    metadata = Metadata(
        title=meta_data.get("title", "Untitled"),
        status=meta_data.get("status", "draft"),
        owner=meta_data.get("owner", "Unknown"),
        description=meta_data.get("description"),
        repository=meta_data.get("repository"),
    )
    
    tiers = []
    for tier_data in data.get("tiers", []):
        tasks = [_parse_task(t) for t in tier_data.get("tasks", [])]
        tier = Tier(
            tier_id=tier_data.get("tier_id", ""),
            name=tier_data.get("name", ""),
            goal=tier_data.get("goal"),
            tasks=tasks,
            status=TierStatus(tier_data.get("status", "not_started")),
        )
        tiers.append(tier)
    
    metrics = []
    for m in data.get("success_metrics", []):
        metrics.append(SuccessMetric(
            metric=m.get("metric", ""),
            target=m.get("target", ""),
            validation=m.get("validation"),
        ))
    
    dep_graph = None
    dg_data = data.get("dependency_graph")
    if dg_data:
        edges = [DependencyEdge(from_task=e["from_task"], to_task=e["to_task"]) for e in dg_data.get("edges", [])]
        groups = []
        for g in dg_data.get("parallelizable_groups", []):
            groups.append(ParallelGroup(
                group_id=g["group_id"],
                tasks=g["tasks"],
                description=g.get("description"),
            ))
        dep_graph = DependencyGraph(
            nodes=dg_data.get("nodes", []),
            edges=edges,
            parallelizable_groups=groups,
        )
    
    return Blueprint(
        blueprint_version=data.get("blueprint_version", "1.3.0"),
        metadata=metadata,
        tiers=tiers,
        strategic_vision=data.get("strategic_vision"),
        success_metrics=metrics,
        dependency_graph=dep_graph,
    )


def _build_dependency_graph(tiers: list[Tier]) -> DependencyGraph:
    """Build dependency graph from parsed tiers."""
    nodes = []
    edges = []
    
    for tier in tiers:
        for task in tier.tasks:
            nodes.append(task.task_id)
            for dep in task.dependencies:
                edges.append(DependencyEdge(from_task=dep, to_task=task.task_id))
    
    return DependencyGraph(nodes=nodes, edges=edges)
