# Blueprint Standard Format Specification

> **Version**: 2.0.1
> **Status**: Stable
> **Last Updated**: 2026-01-05
> **Breaking Changes**: Universal AI Orchestration Contract — output persistence, hand-off protocol, typed dependencies

<!-- BLUEPRINT METADATA (DO NOT REMOVE) -->
<!-- _blueprint_version: 2.0.1 -->
<!-- _generated_at: 2026-01-05T09:35:00Z -->
<!-- _generator: outpost.claude-opus -->
<!-- END METADATA -->

---

## Overview

The Blueprint Standard Format (BSF) v2.0 defines the **Universal AI Orchestration Contract** — a structured, machine-parseable specification enabling seamless multi-agent execution across heterogeneous AI systems (Claude, GPT, Gemini, Grok, DeepSeek, and future models).

**Design Principles** (Fleet-Validated v2.0):
1. **Interface-First, Not Instruction-First** — Contracts over prose
2. **Compilable** — Pre-flight validation before any execution
3. **Structured Format** — Markdown + YAML blocks (canonical: `.bp.yaml`)
4. **Built-in Verification** — Every task is testable at multiple tiers
5. **Human-in-the-Loop Signals** — Explicit pause points
6. **Execution Context** — Agents know HOW to run
7. **Error Policy** — Explicit failure handling
8. **Output Persistence** — Task A output explicitly reaches Task B
9. **Hand-off Protocol** — State checkpoint format with resume semantics
10. **Data Transfer Mechanism** — Explicit stdout/file/memory/network modes

---

## Document Structure

A Blueprint document consists of:

```markdown
# {Project Name} — {Document Type}

> **Document Status**: {status}
> **Last Updated**: {date}
> **Owner**: {owner}

<!-- BLUEPRINT METADATA (DO NOT REMOVE) -->
<!-- _blueprint_version: 2.0.1 -->
<!-- _generated_at: {ISO_8601_TIMESTAMP} -->
<!-- _generator: {generator_identifier} -->
<!-- END METADATA -->

---

## Strategic Vision
{Natural language description of the goal}

---

## Success Metrics
{Table of measurable outcomes}

---

## Execution Configuration
\```yaml
execution:
  shell: bash
  shell_flags: ["-e", "-o", "pipefail"]
  max_parallel_tasks: 4
  resource_locks: []
  preflight_checks: []
\```

---

## Tier N: {Phase Name}

### {Task ID}: {Task Name}

\```yaml
task_id: {unique_id}
name: "{human readable name}"
status: {status_enum}
# ... task block fields
\```

---

## Dependency Graph
\```yaml
dependencies:
  T0.2:
    depends_on: [T0.1]
    input_bindings:
      config: T0.1.output.config_path
\```

---

## Document Control
{Version history}
```

---

## Metadata Block (MANDATORY)

Every Blueprint **must** include a metadata block immediately after the header. This block enables:
- Validation of generated vs manually-written Blueprints
- Version tracking for format compatibility
- Provenance tracking for debugging

### YAML Frontmatter Format (v2.0 Preferred)

```yaml
---
_blueprint_version: "2.0.1"
_generated_at: "2026-01-05T12:00:00Z"
_generator: "blueprint.generator"
_checksum: "sha256:abc123..."
---
```

### HTML Comment Format (v1.x Compatible)

```html
<!-- BLUEPRINT METADATA (DO NOT REMOVE) -->
<!-- _blueprint_version: 2.0.1 -->
<!-- _generated_at: 2026-01-05T12:00:00Z -->
<!-- _generator: blueprint.generator -->
<!-- END METADATA -->
```

| Field | Required | Description |
|-------|----------|-------------|
| `_blueprint_version` | Yes | BSF version used (e.g., "2.0.0") |
| `_generated_at` | Yes | ISO 8601 timestamp of generation |
| `_generator` | Yes | Identifier of generating tool |
| `_checksum` | No | SHA-256 hash for integrity verification |

**Validation Rule**: Documents without this metadata block are considered manually-generated and may fail automated validation.

---

## Execution Configuration (NEW in v2.0)

Global execution settings that apply to all tasks unless overridden.

```yaml
execution:
  # Shell Contract (P1)
  shell: bash                           # Explicit shell specification
  shell_flags: ["-e", "-o", "pipefail"] # Fail-fast by default

  # Parallelization Controls (P1)
  max_parallel_tasks: 4                 # Concurrent task limit
  resource_locks:                       # Named locks for resource contention
    - name: "database"
      type: exclusive
    - name: "gpu"
      type: shared
      max_holders: 2

  # Parallel Group vs Locks Precedence (v2.0.1)
  # See "Parallelization Precedence Rules" section below

  # Preflight Checks (P0)
  preflight_checks:
    - command: "python3 --version"
      expected_exit_code: 0
      error_message: "Python 3 is required"
    - command: "docker info"
      expected_exit_code: 0
      error_message: "Docker must be running"
    - command: "test -f .env"
      expected_exit_code: 0
      error_message: "Missing .env file"

  # Secret Resolution Policy (P0)
  secret_resolution:
    on_missing: abort                   # abort | prompt | skip_task | use_default
    sources:                            # Resolution order
      - type: env
        prefix: ""
      - type: file
        path: ".env"
      - type: vault
        address: "${VAULT_ADDR}"
```

---

## Task Block Schema

Every task is defined in a YAML code block with the following fields:

### Required Fields (Consolidated v2.0.1)

All task blocks require these fields. Fields marked (v2.0+) are new in v2.0.

```yaml
# === CORE FIELDS (v1.x compatible) ===
task_id: string        # Unique identifier (e.g., "T1.2")
name: string           # Human-readable task name
status: enum           # not_started | in_progress | complete | blocked | skipped | checkpointed
dependencies: list     # Task IDs this depends on (empty list if none)

interface:
  input: string        # Human-readable description of required input
  output: string       # Human-readable description of produced output

acceptance_criteria:   # List of testable conditions
  - string

test_command: string   # Shell command that returns 0 on success (see verification block for v2.0)

rollback: string       # Command to undo this task's changes

# === v2.0+ REQUIRED FIELDS ===

# Input Bindings — How this task receives data from dependencies (v2.0+)
input_bindings:
  config:                               # Local binding name
    source: T0.1                        # Source task ID
    output_port: config_path            # Which output from source
    transfer: file                      # stdout | file | memory | network
    required: true                      # Fail if not available

# Output Location — Where this task persists its outputs (v2.0+)
output:
  location: file                        # stdout | file | memory | network
  path: "/tmp/blueprint/${task_id}/output.json"
  ports:                                # Named output ports for consumers
    result:
      type: json

# Required Capabilities — What the executing agent must support (v2.0+)
required_capabilities:
  - python3.11
  - docker
```

### Capability Version Matching (v2.0.2)

Capabilities can specify version constraints using semver-like syntax:

```yaml
required_capabilities:
  - python3.11              # Exact minor version: >=3.11.0 <3.12.0
  - python3                 # Major version: >=3.0.0 <4.0.0
  - node>=18                # Minimum version: >=18.0.0
  - docker>=24.0.0          # Exact minimum: >=24.0.0
  - rust~1.70               # Tilde: >=1.70.0 <1.71.0
  - go^1.21                 # Caret: >=1.21.0 <2.0.0
```

**Version Matching Rules:**

| Syntax | Meaning | Example Match |
|--------|---------|---------------|
| `name` | Any version | `python` matches any Python |
| `name3` | Major version 3.x.x | `python3` matches 3.0.0 to 3.99.99 |
| `name3.11` | Minor version 3.11.x | `python3.11` matches 3.11.0 to 3.11.99 |
| `name>=X.Y.Z` | At least version | `node>=18` matches 18.0.0+ |
| `name~X.Y` | Tilde (patch updates) | `rust~1.70` matches 1.70.0 to 1.70.99 |
| `name^X.Y` | Caret (minor updates) | `go^1.21` matches 1.21.0 to 1.99.99 |
| `name==X.Y.Z` | Exact version | `python==3.11.5` matches only 3.11.5 |

**Version Detection:**

Executors detect capability versions by running:

```yaml
# Detection commands (executor responsibility)
python3: "python3 --version | grep -oP '\\d+\\.\\d+\\.\\d+'"
node: "node --version | grep -oP '\\d+\\.\\d+\\.\\d+'"
docker: "docker --version | grep -oP '\\d+\\.\\d+\\.\\d+'"
go: "go version | grep -oP '\\d+\\.\\d+\\.\\d+'"
rust: "rustc --version | grep -oP '\\d+\\.\\d+\\.\\d+'"
```

**Validation Behavior:**

| Scenario | Preflight Result |
|----------|------------------|
| All capabilities satisfied | ✅ Pass |
| Capability missing | ❌ Fail with `E_CAPABILITY_MISSING` |
| Version too low | ❌ Fail with `E_CAPABILITY_MISSING` (include found vs required) |
| Version detection fails | ⚠️ Warn, attempt execution anyway |

**Field Requirements by Version:**

| Field | v1.x | v2.0+ | Notes |
|-------|------|-------|-------|
| task_id | Required | Required | — |
| name | Required | Required | — |
| status | Required | Required | v2.0 adds `checkpointed` |
| dependencies | Required | Required | v2.0 adds typed bindings |
| interface | Required | Required | v2.0 adds schemas |
| acceptance_criteria | Required | Required | — |
| test_command | Required | Optional | Replaced by `verification` block |
| rollback | Required | Required | — |
| input_bindings | — | Required | New in v2.0 |
| output | — | Required | New in v2.0 |
| required_capabilities | — | Recommended | New in v2.0 |

### Hand-off Block (NEW in v2.0 — P0)

Defines checkpoint/resume semantics for long-running or interruptible tasks.

```yaml
handoff:
  checkpoint_format: json               # json | yaml | binary
  checkpoint_path: "/tmp/blueprint/${task_id}/checkpoint.json"
  checkpoint_interval: PT5M             # ISO 8601 duration
  resume_strategy: from_checkpoint      # from_checkpoint | restart | manual
  
  # Typed state fields (v2.0.1) — What to persist in checkpoint
  state_fields:
    - name: current_step
      path: "$.context.current_step"    # JSONPath to extract from task context
      type: integer
    - name: processed_items
      path: "$.loop.processed_count"
      type: integer
    - name: accumulated_results
      path: "$.results"
      type: array
      items_type: object
  
  # Optional: JSON Schema for checkpoint state validation
  state_schema:
    type: object
    properties:
      current_step: { type: integer, minimum: 0 }
      processed_items: { type: integer, minimum: 0 }
      accumulated_results: { type: array }
    required: [current_step, processed_items]
  
  on_interrupt:
    action: checkpoint                  # checkpoint | abort | ignore
    timeout: PT30S                      # Time to complete checkpoint
```

### Typed State Fields Specification (v2.0.1)

Each state field must declare its extraction path and type for deterministic checkpointing.

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Field name in checkpoint (unique identifier) |
| `path` | Yes | JSONPath expression to extract value from task context |
| `type` | Yes | JSON Schema type: `string`, `integer`, `number`, `boolean`, `array`, `object` |
| `items_type` | If array | Type of array items |
| `default` | No | Default value if path not found |

**Path Resolution:**

```yaml
# Task context structure (provided by executor)
context:
  task_id: "T1.2"
  started_at: "2026-01-05T12:00:00Z"
  working_directory: "/project"
  custom:                               # Task-specific state
    current_step: 3
    batch_size: 100

# State field extraction
state_fields:
  - name: step
    path: "$.custom.current_step"       # Extracts: 3
    type: integer
  - name: batch
    path: "$.custom.batch_size"
    type: integer
    default: 50                         # Used if path not found
```

**Validation Rules:**
1. All state field names must be unique within a handoff block
2. Path must be valid JSONPath syntax
3. Type must match extracted value (or be coercible)
4. If `state_schema` provided, checkpoint must validate against it

### Resources Block (NEW in v2.0 — P1)

Explicit resource requirements and locks.

```yaml
resources:
  cpu: 2                                # vCPU cores
  memory: "4Gi"                         # Memory limit
  gpu: 0                                # GPU count
  disk: "10Gi"                          # Disk space
  locks:                                # Named resource locks
    - name: "database"
      mode: exclusive                   # exclusive | shared
    - name: "gpu"
      mode: shared
  timeout: PT1H                         # ISO 8601 duration (P1 mandate)
```

### Optional Fields (Core)

```yaml
assignee: string|null           # Agent or human assigned
estimated_sessions: integer     # Estimated work sessions
files_to_create: list           # Files this task will produce
files_to_modify: list           # Existing files to change
notes: string                   # Additional context
example: object                 # Example input/output for clarity
idempotent: boolean             # Whether task is safe to re-run (v2.0.2)
```

### Idempotency Declaration (v2.0.2)

Tasks can declare whether they are idempotent (safe to re-run without side effects).

```yaml
idempotent: true                # Safe to re-run — executor may retry freely
idempotent: false               # Not idempotent — executor must checkpoint before retry
```

**Idempotency Guidelines:**

| Idempotent | Examples | Retry Behavior |
|------------|----------|----------------|
| `true` | File writes, GET requests, pure functions | Re-run from start on failure |
| `false` | Database inserts, POST requests, file appends | Checkpoint before retry, resume from state |

**Executor Behavior:**

| idempotent | on_failure.action | Behavior |
|------------|-------------------|----------|
| `true` | retry | Re-execute from beginning |
| `false` | retry | Save checkpoint, then re-execute from checkpoint |
| `true` | block | Mark blocked (no retry) |
| `false` | block | Save checkpoint, mark blocked |

**Default:** If `idempotent` is not specified, executor assumes `false` (conservative).

**Validation Rules:**
1. Tasks with `idempotent: false` SHOULD have `handoff.checkpoint_format` defined
2. Tasks with `idempotent: false` and `on_failure.max_retries > 0` MUST support checkpointing

### Optional Fields (Execution Context)

```yaml
execution_context:
  working_directory: string     # Absolute path for command execution
  environment_variables:        # Env vars required for execution
    KEY: "value"
    SECRET_REF: "${secrets.NAME}"  # Reference to secret (not actual value)
  required_tools: list          # Tools that must be available
    - "python3"
    - "pytest"
    - "npm"
  timeout: PT1H                 # ISO 8601 duration (v2.0: mandate PT format)
  setup_command: string         # Run before test_command (install deps, etc.)
  shell_override: zsh           # Override global shell for this task
```

### Timeout Precedence (v2.0.1)

**Problem:** Timeout can appear in multiple places:
- `resources.timeout` — Task-level resource limit
- `execution_context.timeout` — Execution environment limit  
- `human_required.timeout` — Human response timeout
- `verification.*.timeout` — Per-verification-tier timeout
- `handoff.on_interrupt.timeout` — Checkpoint save timeout

**Resolution — Precedence Order (highest to lowest):**

| Priority | Location | Scope | Default |
|----------|----------|-------|---------|
| 1 | `verification.*.timeout` | Per-test | PT2M |
| 2 | `resources.timeout` | Entire task | PT1H |
| 3 | `execution_context.timeout` | Task execution | Inherits from resources |
| 4 | `human_required.timeout` | Human response | PT24H |
| 5 | `handoff.on_interrupt.timeout` | Checkpoint save | PT30S |

**Rules:**
1. More specific timeouts override less specific
2. `resources.timeout` is the master task timeout — task fails if exceeded regardless of other timeouts
3. `verification.*.timeout` applies per verification tier, not cumulative
4. If `execution_context.timeout` not set, inherits from `resources.timeout`
5. `human_required.timeout` runs independently (clock starts when human action requested)

**Example:**
```yaml
resources:
  timeout: PT1H                    # Master: task must complete in 1 hour

execution_context:
  timeout: PT30M                   # Execution phase: 30 minutes (overrides inheritance)

verification:
  smoke:
    timeout: PT10S                 # Smoke test: 10 seconds
  unit:
    timeout: PT5M                  # Unit tests: 5 minutes (separate from smoke)

human_required:
  timeout: PT24H                   # Wait up to 24 hours for human (independent clock)
```

### Optional Fields (Typed Interface)

```yaml
interface:
  input: string                 # Human-readable (required)
  output: string                # Human-readable (required)
  input_type: string            # "json" | "yaml" | "text" | "file_path" | "none"
  output_type: string           # "json" | "yaml" | "text" | "file_path" | "none"
  input_schema:                 # JSON Schema for validation (P1: required for chains)
    type: object
    properties:
      field_name: { type: "string" }
    required: ["field_name"]
  output_schema:                # JSON Schema for validation
    type: object
    properties:
      result: { type: "boolean" }
  example_input: string         # Concrete example (JSON string or value)
  example_output: string        # Concrete example (JSON string or value)
```

### Optional Fields (Error Policy)

```yaml
on_failure:
  max_retries: integer          # Number of retry attempts (default: 0)
  retry_delay: PT10S            # ISO 8601 duration (default: PT5S)
  action: enum                  # "block" | "abort" | "skip" (default: "block")
    # block: Mark task blocked, continue other independent tasks
    # abort: Stop entire Blueprint execution
    # skip: Mark task skipped, proceed to dependents anyway
  fallback_task: T1.2.fallback  # Optional task to run on failure

on_success: string              # Optional command to run after success
```

### Error Message Schema (v2.0.2)

When tasks fail, executors MUST produce structured error messages conforming to this schema:

```yaml
error:
  code: string                  # Machine-readable error code (e.g., "E_VALIDATION_FAILED")
  message: string               # Human-readable error description
  task_id: string               # Task that failed
  phase: enum                   # "preflight" | "setup" | "execution" | "verification" | "cleanup"
  timestamp: string             # ISO 8601 timestamp of failure
  details:                      # Optional structured details
    exit_code: integer          # Process exit code (if applicable)
    stdout: string              # Captured stdout (truncated to 10KB)
    stderr: string              # Captured stderr (truncated to 10KB)
    duration: string            # ISO 8601 duration of failed operation
  cause: object                 # Optional nested error (for chained failures)
  retry_info:                   # Present if retries were attempted
    attempt: integer            # Which attempt failed (1-indexed)
    max_attempts: integer       # Total attempts allowed
    will_retry: boolean         # Whether another retry will occur
```

**Standard Error Codes:**

| Code | Phase | Description |
|------|-------|-------------|
| `E_PREFLIGHT_FAILED` | preflight | Preflight check did not pass |
| `E_DEPENDENCY_MISSING` | preflight | Required dependency task not complete |
| `E_SECRET_MISSING` | preflight | Required secret not resolvable |
| `E_CAPABILITY_MISSING` | preflight | Required capability not available |
| `E_SETUP_FAILED` | setup | setup_command exited non-zero |
| `E_EXECUTION_FAILED` | execution | Task execution error |
| `E_TIMEOUT` | execution | Task exceeded timeout |
| `E_VERIFICATION_FAILED` | verification | test_command/verification exited non-zero |
| `E_ROLLBACK_FAILED` | cleanup | Rollback command failed |
| `E_LOCK_TIMEOUT` | execution | Could not acquire resource lock |
| `E_CHECKPOINT_FAILED` | execution | Failed to save checkpoint |

**Example Error:**

```json
{
  "code": "E_VERIFICATION_FAILED",
  "message": "Unit tests failed with 3 failures",
  "task_id": "T1.2",
  "phase": "verification",
  "timestamp": "2026-01-05T14:30:00Z",
  "details": {
    "exit_code": 1,
    "stdout": "...",
    "stderr": "FAILED tests/test_jwt.py::test_expired_token - AssertionError",
    "duration": "PT45S"
  },
  "retry_info": {
    "attempt": 2,
    "max_attempts": 3,
    "will_retry": true
  }
}
```

### Logging Format Specification (v2.0.2)

Executors SHOULD produce structured logs conforming to this specification for observability and debugging.

```yaml
execution:
  logging:
    format: json                      # json | text | ndjson
    level: info                       # debug | info | warn | error
    destination: stdout               # stdout | stderr | file | syslog
    file_path: "/var/log/blueprint/${blueprint_id}.log"  # If destination: file
    include_timestamps: true
    include_task_context: true        # Add task_id to every log line
```

**Log Entry Schema (JSON format):**

```json
{
  "timestamp": "2026-01-05T14:30:00.123Z",
  "level": "info",
  "blueprint_id": "bp-2026-01-05-001",
  "task_id": "T1.2",
  "executor_id": "exec-abc123",
  "phase": "execution",
  "message": "Starting task execution",
  "data": {}
}
```

**Log Levels:**

| Level | Use Case |
|-------|----------|
| `debug` | Detailed debugging info (variable values, internal state) |
| `info` | Normal operational messages (task start/complete, checkpoints) |
| `warn` | Warnings that don't fail execution (retry attempts, deprecations) |
| `error` | Errors that affect execution (task failures, validation errors) |

**Required Log Events:**

| Event | Level | When |
|-------|-------|------|
| `blueprint.start` | info | Blueprint execution begins |
| `blueprint.complete` | info | Blueprint execution succeeds |
| `blueprint.failed` | error | Blueprint execution fails |
| `task.start` | info | Task begins execution |
| `task.complete` | info | Task completes successfully |
| `task.failed` | error | Task fails (after retries exhausted) |
| `task.retry` | warn | Task retry attempt |
| `task.checkpoint` | info | Checkpoint saved |
| `task.resume` | info | Resuming from checkpoint |
| `lock.acquired` | debug | Resource lock obtained |
| `lock.released` | debug | Resource lock released |

**Text Format (when format: text):**

```
2026-01-05T14:30:00.123Z [INFO] [T1.2] Starting task execution
2026-01-05T14:30:45.456Z [ERROR] [T1.2] Task failed: E_VERIFICATION_FAILED
```

### Optional Fields (Human-in-the-Loop)

```yaml
human_required:
  action: string                # What the human must do
  reason: string                # Why it's needed
  notify:
    channel: string             # "email" | "slack" | "webhook" | "env" | "console"
    recipient: string           # Email/channel for email/slack
    variable: string            # Env var name for "env" channel
    url: string                 # URL for webhook channel
  timeout: PT24H                # ISO 8601 duration (v2.0 mandate)
  on_timeout: string            # "abort" | "skip" | "continue" (default: "abort")
  on_missing: string            # For env channel: action if var not set
```

### Tiered Verification (NEW in v2.0 — P1)

```yaml
verification:
  # Tier 1: Quick smoke test (< 10 seconds)
  smoke:
    command: "python -c 'from src.auth import jwt; print(\"OK\")'"
    timeout: PT10S

  # Tier 2: Unit tests (< 2 minutes)
  unit:
    command: "pytest tests/unit/test_jwt.py -v"
    timeout: PT2M

  # Tier 3: Integration tests (< 10 minutes)
  integration:
    command: "pytest tests/integration/ -v --tb=short"
    timeout: PT10M
    requires_resources: [database]

  # Tier 4: End-to-end (< 30 minutes)
  e2e:
    command: "pytest tests/e2e/ -v"
    timeout: PT30M
    requires_resources: [database, redis]
    optional: true              # Don't fail task if e2e fails

# Legacy support — maps to verification.unit
test_command: string
```

### test_command vs verification Resolution (v2.0.1)

**Problem:** Both `test_command` and `verification` block exist. Unclear which takes precedence.

**Resolution:**

| Scenario | Behavior |
|----------|----------|
| Only `test_command` present | Use as `verification.unit` (v1.x compatibility) |
| Only `verification` present | Use verification block (v2.0 preferred) |
| Both present | `verification` block takes precedence; `test_command` ignored with warning |
| Neither present | Validation error (at least one required) |

**Migration Path:**
```yaml
# v1.x style (deprecated but supported)
test_command: "pytest tests/ -v"

# v2.0 style (preferred)
verification:
  unit:
    command: "pytest tests/ -v"
    timeout: PT2M
```

**Validation Rule:** If both `test_command` and `verification.unit` are present, they must be identical or validator emits a warning.

---

## Status Enumeration

**IMPORTANT: Use lowercase text values only. Emoji prefixes are for display, not serialization.**

| Status | Value | Meaning |
|--------|-------|---------|
| Not Started | `not_started` | Task has not begun |
| In Progress | `in_progress` | Task is actively being worked |
| Complete | `complete` | Task finished and verified |
| Blocked | `blocked` | Task cannot proceed (dependency or human required) |
| Skipped | `skipped` | Task intentionally bypassed |
| **Checkpointed** | `checkpointed` | Task paused with saved state (NEW v2.0) |

Display icons (optional, for human readability):
- 🔲 not_started
- 🔄 in_progress
- ✅ complete
- ⛔ blocked
- ⏭️ skipped
- 💾 checkpointed

### Status Transition Rules (v2.0.1)

**Problem:** The `checkpointed` status was added in v2.0 but valid transitions were undefined.

**State Machine:**

```
                    ┌─────────────────────────────────────┐
                    │                                     │
                    ▼                                     │
┌─────────────┐   start   ┌─────────────┐   interrupt   ┌─────────────┐
│ not_started │ ────────► │ in_progress │ ────────────► │ checkpointed│
└─────────────┘           └─────────────┘               └─────────────┘
                                │                             │
                                │ complete                    │ resume
                                ▼                             │
                          ┌─────────────┐                     │
                          │  complete   │ ◄───────────────────┘
                          └─────────────┘         (via in_progress)
```

**Valid Transitions:**

| From | To | Trigger | Description |
|------|----|---------|-------------|
| `not_started` | `in_progress` | Task execution begins | Normal start |
| `not_started` | `skipped` | Skip directive | Intentional bypass |
| `in_progress` | `complete` | Verification passes | Normal completion |
| `in_progress` | `blocked` | Dependency fails / human required | Waiting state |
| `in_progress` | `checkpointed` | Interrupt signal / checkpoint_interval | State saved |
| `in_progress` | `skipped` | Skip directive mid-execution | Intentional abort |
| `checkpointed` | `in_progress` | Resume (from_checkpoint) | Continue from saved state |
| `checkpointed` | `not_started` | Resume (restart) | Discard checkpoint, start fresh |
| `blocked` | `in_progress` | Blocker resolved | Resume after unblock |
| `blocked` | `skipped` | Skip directive | Give up on blocked task |

**Invalid Transitions (must fail validation):**

| From | To | Reason |
|------|----|--------|
| `complete` | Any | Terminal state — completed tasks cannot change |
| `skipped` | Any | Terminal state — skipped tasks cannot resume |
| `not_started` | `complete` | Must go through `in_progress` |
| `not_started` | `checkpointed` | Cannot checkpoint without starting |
| `checkpointed` | `complete` | Must resume to `in_progress` first |
| `checkpointed` | `blocked` | Must resume to `in_progress` first |

**Executor Behavior:**

```yaml
# On interrupt (SIGTERM, timeout, manual pause)
if task.status == "in_progress" and task.handoff.on_interrupt.action == "checkpoint":
    save_checkpoint(task)
    task.status = "checkpointed"

# On resume
if task.status == "checkpointed":
    if task.handoff.resume_strategy == "from_checkpoint":
        load_checkpoint(task)
        task.status = "in_progress"
    elif task.handoff.resume_strategy == "restart":
        discard_checkpoint(task)
        task.status = "not_started"
    elif task.handoff.resume_strategy == "manual":
        await human_decision(task)
```

---

## Output Persistence (NEW in v2.0 — P0)

Tasks must explicitly declare how they persist outputs for downstream consumers.

### Transfer Mechanisms

| Mechanism | Use Case | Persistence |
|-----------|----------|-------------|
| `stdout` | Simple text/JSON output | Captured by executor |
| `file` | Large artifacts, binaries | Written to specified path |
| `memory` | Fast inter-task data | In-process (same executor) |
| `network` | Distributed execution | See Network Transfer Specification below |

### Memory Transfer Fallback Rule (v2.0.1)

**Problem:** Memory transfer (`transfer: memory`) only works when tasks execute within the same process/executor. When execution crosses executor boundaries (agent hand-off, parallel dispatch to different agents), memory transfer fails silently.

**Solution:** Automatic fallback to file transfer with JSON serialization.

```yaml
# Input binding with memory transfer and fallback
input_bindings:
  data:
    source: T0.1
    output_port: parsed_data
    transfer: memory
    fallback:
      transfer: file
      format: json                      # json | yaml | pickle (json recommended)
      path: "/tmp/blueprint/${source_task_id}/${output_port}.json"
```

**Fallback Behavior:**

| Condition | Behavior |
|-----------|----------|
| Same executor, memory available | Use memory transfer (fast path) |
| Different executor, `fallback` defined | Auto-convert to file transfer |
| Different executor, no `fallback` | **FAIL** with clear error |
| Memory transfer with non-serializable data | **FAIL** at preflight |

**Default Fallback (when not specified):**

If `fallback` is omitted on a memory transfer, executors **SHOULD** use this default:

```yaml
fallback:
  transfer: file
  format: json
  path: "/tmp/blueprint/fallback/${source_task_id}/${output_port}.json"
```

**Validation Rules:**
1. Memory transfer with `agent_handoff.allowed: true` MUST have fallback defined
2. Fallback format must be serialization-compatible with output type
3. Fallback path must be writable by both source and consuming tasks

### Network Transfer Specification (v2.0.1)

When `transfer: network` is used, additional fields specify the protocol and endpoint.

```yaml
output:
  location: network
  network:
    protocol: s3                        # REQUIRED: s3 | http | https | sqs | kafka
    endpoint: "s3://blueprint-artifacts/${task_id}/output.json"
    auth:
      type: aws_credentials             # aws_credentials | bearer_token | api_key | none
      secret_ref: "${secrets.AWS_CREDS}"
    timeout: PT30S                      # Connection/upload timeout
    retry:
      max_attempts: 3
      delay: PT5S
```

**Supported Protocols:**

| Protocol | Endpoint Format | Auth Types | Use Case |
|----------|-----------------|------------|----------|
| `s3` | `s3://bucket/path` | aws_credentials | Large artifacts, cross-region |
| `http` | `http://host/path` | bearer_token, api_key, none | Internal services |
| `https` | `https://host/path` | bearer_token, api_key, none | External APIs |
| `sqs` | `sqs://queue-url` | aws_credentials | Async message passing |
| `kafka` | `kafka://broker/topic` | api_key, none | Event streaming |

**Auth Type Specifications:**

```yaml
# AWS Credentials (for s3, sqs)
auth:
  type: aws_credentials
  secret_ref: "${secrets.AWS_ACCESS_KEY}"  # References AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY

# Bearer Token (for http, https)
auth:
  type: bearer_token
  secret_ref: "${secrets.API_TOKEN}"

# API Key (for http, https, kafka)
auth:
  type: api_key
  header: "X-API-Key"                   # Header name (default: Authorization)
  secret_ref: "${secrets.API_KEY}"

# No Auth
auth:
  type: none
```

**Validation Rules:**
1. `protocol` is required when `location: network`
2. `endpoint` must match protocol format
3. `auth.secret_ref` must be resolvable via secret_resolution policy
4. `timeout` defaults to PT30S if not specified

### Output Declaration

```yaml
output:
  location: file
  path: "/tmp/blueprint/${task_id}/output.json"
  format: json                          # json | yaml | text | binary
  ports:
    # Named outputs that other tasks can bind to
    config_path:
      type: file_path
      value: "${working_directory}/config.json"
    parsed_data:
      type: json
      schema:
        type: object
        properties:
          items: { type: array }
    status:
      type: text
      value: "success"
```

### Output Cleanup and TTL (v2.0.1)

**Problem:** Task outputs persist indefinitely with no cleanup specification, leading to disk exhaustion on long-running or repeated Blueprint executions.

**Solution:** Add optional `cleanup` block to output declaration.

```yaml
output:
  location: file
  path: "/tmp/blueprint/${task_id}/output.json"
  format: json
  cleanup:
    ttl: PT24H                          # ISO 8601 duration — auto-delete after 24 hours
    policy: after_consumers             # When to start TTL countdown
    on_blueprint_complete: delete       # Action when Blueprint finishes
```

**Cleanup Policies:**

| Policy | TTL Starts | Description |
|--------|------------|-------------|
| `after_creation` | When output file is written | Absolute TTL from creation |
| `after_consumers` | When all consuming tasks complete | Wait for dependents first |
| `after_blueprint` | When entire Blueprint completes | Keep until execution ends |
| `never` | N/A | Persist indefinitely (explicit opt-out) |

**Blueprint Completion Actions:**

| Action | Behavior |
|--------|----------|
| `delete` | Remove output files when Blueprint completes successfully |
| `keep` | Preserve outputs indefinitely |
| `archive` | Move to archive location (if `archive_path` specified) |

**Extended Example:**

```yaml
output:
  location: file
  path: "/tmp/blueprint/${task_id}/output.json"
  format: json
  cleanup:
    ttl: PT1H                           # Delete 1 hour after consumers complete
    policy: after_consumers
    on_blueprint_complete: delete       # Delete on success
    on_blueprint_failure: keep          # Preserve for debugging on failure
    archive_path: "s3://blueprint-archive/${blueprint_id}/${task_id}/"
```

**Default Behavior (when cleanup not specified):**

```yaml
cleanup:
  ttl: null                             # No automatic expiration
  policy: after_blueprint
  on_blueprint_complete: keep           # Preserve by default (safe)
  on_blueprint_failure: keep
```

**Validation Rules:**
1. `ttl` must be valid ISO 8601 duration (e.g., `PT1H`, `P7D`)
2. `archive_path` required if `on_blueprint_complete: archive`
3. Executor SHOULD log cleanup actions for auditability
4. Executor MUST NOT delete outputs still needed by pending consumers

**Executor Responsibility:**
- Track output file creation timestamps
- Track consumer task completion
- Run cleanup based on policy and TTL
- Handle cleanup failures gracefully (log warning, continue)

### Input Binding

```yaml
input_bindings:
  # Bind "config" to T0.1's "config_path" output
  config:
    source: T0.1
    output_port: config_path
    transfer: file
    required: true
    transform: null                     # No transformation

  # Bind "data" to T0.2's "parsed_data" output with transformation
  data:
    source: T0.2
    output_port: parsed_data
    transfer: memory
    required: true
    transform:
      language: jq                      # REQUIRED: jq (canonical)
      expression: ".items[0]"           # jq expression to apply
```

### Transform Language Specification (v2.0.1)

Blueprint uses **jq** as the canonical transform language for input binding transformations.

| Field | Required | Description |
|-------|----------|-------------|
| `language` | Yes | Transform language identifier. Must be `jq`. |
| `expression` | Yes | The transformation expression |

**Why jq?**
- Fleet consensus: 5/5 agents support jq
- Well-defined semantics with official specification
- Widely available (preinstalled on most CI systems)
- Predictable behavior across implementations

**Validation Rules:**
1. If `transform` is not null, both `language` and `expression` are required
2. `language` must be `jq` (future versions may add `jsonpath`)
3. Expression must be valid jq syntax (validated at preflight)

**Examples:**
```yaml
# Extract first item from array
transform:
  language: jq
  expression: ".items[0]"

# Filter and map
transform:
  language: jq
  expression: ".users | map(select(.active)) | .[].email"

# Extract nested field with default
transform:
  language: jq
  expression: ".config.timeout // 30"
```

---

## Hand-off Protocol (NEW in v2.0 — P0)

Enables task interruption, checkpointing, and resumption across agent sessions.

### Checkpoint Format

```json
{
  "blueprint_version": "2.0.0",
  "task_id": "T1.2",
  "checkpoint_id": "chk-2026-01-05-001",
  "created_at": "2026-01-05T12:30:00Z",
  "state": {
    "current_step": 3,
    "processed_items": 150,
    "accumulated_results": { ... }
  },
  "resume_instructions": "Continue from step 3 with item 151",
  "executor_hints": {
    "last_successful_command": "python process.py --batch 3",
    "next_command": "python process.py --batch 4"
  }
}
```

### Resume Semantics

| Strategy | Behavior |
|----------|----------|
| `from_checkpoint` | Load checkpoint, continue from saved state |
| `restart` | Ignore checkpoint, start from beginning |
| `manual` | Present checkpoint to human, await instructions |

### Hand-off Block

```yaml
handoff:
  checkpoint_format: json
  checkpoint_path: "/tmp/blueprint/${task_id}/checkpoint.json"
  checkpoint_interval: PT5M             # Auto-checkpoint every 5 minutes
  resume_strategy: from_checkpoint

  # Typed state fields (v2.0.1)
  state_fields:
    - name: current_step
      path: "$.context.step"
      type: integer
    - name: processed_items
      path: "$.context.processed"
      type: integer
    - name: error_count
      path: "$.context.errors"
      type: integer
      default: 0

  # Behavior on SIGTERM/interruption
  on_interrupt:
    action: checkpoint                  # Save state before exit
    timeout: PT30S                      # Max time to save

  # Agent hand-off (different agent resumes)
  agent_handoff:
    allowed: true
    required_context:                   # What resuming agent needs
      - checkpoint_file
      - source_code
      - test_results
```

### Checkpoint Conflict Resolution (v2.0.2)

When multiple executors or resume attempts create checkpoint conflicts, this defines resolution behavior.

```yaml
handoff:
  conflict_resolution: last_write_wins  # last_write_wins | optimistic_lock | manual
  checkpoint_versioning: true           # Include version in checkpoint
```

**Conflict Scenarios:**

| Scenario | Description |
|----------|-------------|
| Concurrent write | Two executors write checkpoint for same task simultaneously |
| Stale resume | Executor resumes from outdated checkpoint |
| Split brain | Task runs on two executors due to network partition |

**Resolution Strategies:**

| Strategy | Behavior | Use Case |
|----------|----------|----------|
| `last_write_wins` | Latest timestamp wins, older discarded | Simple, fast, eventual consistency |
| `optimistic_lock` | Check version before write, fail if stale | Strong consistency, may require retry |
| `manual` | Pause for human decision | Critical tasks, data integrity paramount |

**Checkpoint Versioning:**

When `checkpoint_versioning: true`, checkpoint includes version metadata:

```json
{
  "version": 3,
  "previous_version": 2,
  "created_at": "2026-01-05T14:30:00Z",
  "executor_id": "exec-abc123",
  "state": { ... }
}
```

**Optimistic Lock Algorithm:**

```yaml
# Write checkpoint
1. Read current checkpoint version (V)
2. Prepare new checkpoint with version = V + 1
3. Atomic write with condition: current_version == V
4. If condition fails → conflict detected:
   a. Re-read checkpoint
   b. Merge state (if possible) or abort
   c. Retry from step 1
```

**Default:** `conflict_resolution: last_write_wins` (simple, works for most cases)

---

## Secret Resolution (NEW in v2.0 — P0)

Explicitly defines behavior when secrets are unavailable.

### Resolution Chain

```yaml
execution:
  secret_resolution:
    on_missing: abort                   # abort | prompt | skip_task | use_default
    sources:
      - type: env                       # Check environment variables
        prefix: ""
      - type: file                      # Check .env file
        path: ".env"
      - type: vault                     # Check HashiCorp Vault
        address: "${VAULT_ADDR}"
        path: "secret/data/blueprint"
      - type: aws_ssm                   # Check AWS Parameter Store
        prefix: "/blueprint/"
```

### Secret Reference Format

```yaml
environment_variables:
  DATABASE_URL: "${secrets.DATABASE_URL}"           # Standard format
  API_KEY: "${secrets.ANTHROPIC_API_KEY:default}"   # With default value
  OPTIONAL: "${secrets.OPTIONAL_KEY:}"              # Empty string if missing
```

### Missing Secret Behaviors

| Action | Behavior |
|--------|----------|
| `abort` | Fail Blueprint immediately with clear error |
| `prompt` | Trigger `human_required` to provide secret |
| `skip_task` | Skip tasks requiring the secret |
| `use_default` | Use default value if provided |

---

## Interface Satisfiability (NEW in v2.0 — P1)

Interfaces must be provably satisfiable at validation time.

### Exact Key Mapping

When a task depends on another, the validator checks:
1. Output ports exist on the source task
2. Output types match input expectations
3. Schemas are compatible (if provided)

```yaml
# Task T0.1 output
output:
  ports:
    config:
      type: json
      schema:
        type: object
        properties:
          database_url: { type: string }
          cache_ttl: { type: integer }
        required: [database_url]

# Task T0.2 input binding — VALID
input_bindings:
  settings:
    source: T0.1
    output_port: config              # ✅ Exists
    required: true

# Task T0.3 input binding — INVALID
input_bindings:
  settings:
    source: T0.1
    output_port: configuration       # ❌ Port doesn't exist (typo)
```

### Validation Rules

1. All `output_port` references must exist on source task
2. If `input_schema` provided, source `output_schema` must be compatible (see below)
3. `required: true` bindings must have reachable source tasks
4. Circular dependencies are forbidden

### Schema Compatibility Definition (v2.0.1)

Two JSON Schemas are **compatible** when the output schema can satisfy the input schema requirements.

**Compatibility Algorithm:**

```
COMPATIBLE(output_schema, input_schema) → boolean:

1. If input_schema is not defined → COMPATIBLE (no constraints)
2. If output_schema is not defined but input_schema is → INCOMPATIBLE
3. For each required field in input_schema:
   a. Field must exist in output_schema
   b. Types must be compatible per TYPE_COMPATIBLE rules
4. Optional fields in input_schema need not exist in output_schema
5. Extra fields in output_schema are allowed (open-world assumption)
```

**Type Compatibility Rules:**

| Input Type | Compatible Output Types |
|------------|------------------------|
| `string` | `string` |
| `integer` | `integer` |
| `number` | `number`, `integer` (integer is subset of number) |
| `boolean` | `boolean` |
| `array` | `array` (item types must be compatible) |
| `object` | `object` (nested compatibility check) |
| `null` | `null`, or any type with `nullable: true` |
| `any` | Any type |

**Coercion Rules (optional, executor-dependent):**

| From | To | Coercion |
|------|----|----------|
| `integer` | `string` | `String(value)` |
| `number` | `string` | `String(value)` |
| `boolean` | `string` | `"true"` / `"false"` |
| `string` | `integer` | `parseInt(value)` if valid |
| `string` | `number` | `parseFloat(value)` if valid |
| `string` | `boolean` | `"true"` → true, `"false"` → false |

**Examples:**

```yaml
# COMPATIBLE: Output has all required input fields
output_schema:
  type: object
  properties:
    user_id: { type: string }
    email: { type: string }
    created_at: { type: string }      # Extra field OK
  required: [user_id, email]

input_schema:
  type: object
  properties:
    user_id: { type: string }
    email: { type: string }
  required: [user_id]                 # email optional in consumer

# Result: ✅ COMPATIBLE

# INCOMPATIBLE: Missing required field
output_schema:
  type: object
  properties:
    user_id: { type: string }
  required: [user_id]

input_schema:
  type: object
  properties:
    user_id: { type: string }
    email: { type: string }
  required: [user_id, email]          # email required but not in output

# Result: ❌ INCOMPATIBLE (missing required field: email)

# INCOMPATIBLE: Type mismatch
output_schema:
  type: object
  properties:
    count: { type: string }           # String type
  required: [count]

input_schema:
  type: object
  properties:
    count: { type: integer }          # Expects integer
  required: [count]

# Result: ❌ INCOMPATIBLE (type mismatch: string vs integer)
# Note: May be COMPATIBLE if executor enables coercion
```

**Validation Behavior:**

| Scenario | Preflight | Runtime |
|----------|-----------|---------|
| Schemas compatible | ✅ Pass | Execute normally |
| Schemas incompatible | ❌ Fail | Never reaches runtime |
| Output schema missing | ⚠️ Warn | Runtime type check |
| Input schema missing | ✅ Pass | No validation |

---

## Structured Dependency Graph (NEW in v2.0 — P2)

### YAML Dependency Map

```yaml
dependency_graph:
  T0.1:
    depends_on: []

  T0.2:
    depends_on: [T0.1]
    input_bindings:
      config: T0.1.output.config_path

  T0.3:
    depends_on: [T0.1, T0.2]
    input_bindings:
      schema: T0.1.output.schema_file
      migrations: T0.2.output.migration_list

  T1.1:
    depends_on: [T0.3]
    parallel_group: "api_layer"       # Tasks in same group can run parallel

  T1.2:
    depends_on: [T0.3]
    parallel_group: "api_layer"
```

### Visual Representation

```
T0.1 ─┬─► T0.2 ─┬─► T0.3 ─┬─► T1.1 [api_layer]
      │         │         │
      └─────────┘         └─► T1.2 [api_layer]
```

### Typed Dependency References

```yaml
dependencies:
  - task: T0.1
    type: data                          # data | completion | resource
    output_port: config_path

  - task: T0.2
    type: completion                    # Only need T0.2 to finish, no data

  - task: T0.3
    type: resource                      # Release resource lock after T0.3
    resource: database
```

### Dependency Source of Truth (v2.0.1)

**Problem:** Dependencies can be specified in three places:
1. `dependencies` list (task-level)
2. `input_bindings` (task-level)
3. `dependency_graph` (document-level)

**Resolution — Single Source of Truth:**

| Location | Purpose | Authoritative For |
|----------|---------|-------------------|
| `input_bindings` | Data flow dependencies | **Data dependencies** (what data flows where) |
| `dependencies` | Completion-only dependencies | **Ordering** (tasks with no data flow) |
| `dependency_graph` | Document-level view | **Computed** (validator generates from above) |

**Rules:**
1. `input_bindings` is authoritative for data dependencies — if task B needs data from task A, use `input_bindings`
2. `dependencies` list is for completion-only dependencies — task B must wait for A, but no data flows
3. `dependency_graph` at document level is **computed/validated**, not authored — validator generates it from task-level declarations
4. If `dependency_graph` is authored, validator checks consistency with task-level declarations

**Example:**
```yaml
# Task T0.2 — CORRECT: use input_bindings for data dependency
input_bindings:
  config:
    source: T0.1
    output_port: config_path
dependencies: []  # No completion-only deps needed; input_bindings implies T0.1 dependency

# Task T0.3 — CORRECT: use dependencies for completion-only
input_bindings: {}
dependencies: [T0.2]  # Wait for T0.2 to complete, but no data needed

# INCORRECT: Don't duplicate
input_bindings:
  config:
    source: T0.1
dependencies: [T0.1]  # ❌ Redundant — input_bindings already implies this
```

### Parallelization Precedence Rules (v2.0.1)

**Problem:** Tasks in the same `parallel_group` are intended to run in parallel. However, if they require conflicting resource locks (e.g., both need exclusive access to "database"), which constraint takes precedence?

**Resolution: Resource locks ALWAYS take precedence over parallel_group membership.**

**Precedence Order (highest to lowest):**

| Priority | Constraint | Behavior |
|----------|------------|----------|
| 1 | `resources.locks` (exclusive) | Task waits for exclusive lock — never parallelized with holder |
| 2 | `resources.locks` (shared) | Task runs if under `max_holders` limit |
| 3 | `max_parallel_tasks` | Global concurrency cap — tasks queue if at limit |
| 4 | `parallel_group` | Tasks in same group CAN run parallel (if locks allow) |
| 5 | `dependencies` | Tasks wait for dependencies regardless of group |

**Example:**

```yaml
# T1.1 and T1.2 are in same parallel_group but have lock conflict
T1.1:
  parallel_group: "api_layer"
  resources:
    locks:
      - name: "database"
        mode: exclusive          # Needs exclusive DB access

T1.2:
  parallel_group: "api_layer"
  resources:
    locks:
      - name: "database"
        mode: exclusive          # Also needs exclusive DB access

# Result: T1.1 and T1.2 CANNOT run in parallel despite same group
# Lock precedence overrides parallel_group
```

**Executor Behavior:**

```yaml
# Scheduling algorithm (pseudocode)
for task in ready_tasks:
    if not dependencies_satisfied(task):
        skip  # Wait for deps

    if task.resources.locks:
        for lock in task.resources.locks:
            if lock.mode == "exclusive" and lock.held_by_any():
                queue(task)  # Wait for lock release
            if lock.mode == "shared" and lock.holders >= lock.max_holders:
                queue(task)  # Wait for slot

    if running_tasks_count >= max_parallel_tasks:
        queue(task)  # Global limit reached

    # All constraints satisfied — run task
    execute(task)
```

**Validation Rules:**
1. Executor MUST NOT run two tasks holding the same exclusive lock simultaneously
2. Executor MUST respect `max_parallel_tasks` even if `parallel_group` allows more
3. `parallel_group` is a HINT for potential parallelism, not a guarantee
4. Locks are acquired at task start, released at task completion (or checkpoint)

---

## Canonical File Format (NEW in v2.0 — P2)

### `.bp.yaml` Format

Pure YAML format for machine consumption and programmatic generation.

```yaml
# blueprint.bp.yaml
---
_blueprint_version: "2.0.1"
_generated_at: "2026-01-05T12:00:00Z"
_generator: "blueprint.generator"

metadata:
  name: "User Authentication System"
  status: active
  owner: "Platform Team"

strategic_vision: |
  Implement a secure, scalable user authentication system
  with JWT tokens and role-based access control.

success_metrics:
  - metric: "Authentication latency"
    target: "< 100ms p99"
  - metric: "Token validation accuracy"
    target: "100%"

execution:
  shell: bash
  shell_flags: ["-e", "-o", "pipefail"]
  max_parallel_tasks: 4

tiers:
  - name: "Foundation"
    tier_number: 0
    tasks:
      - task_id: T0.1
        name: "Setup project structure"
        status: not_started
        dependencies: []
        interface:
          input: "Project requirements document"
          output: "Initialized project with directory structure"
        output:
          location: file
          ports:
            project_root:
              type: file_path
        acceptance_criteria:
          - "pyproject.toml exists"
          - "src/ directory created"
        verification:
          smoke:
            command: "test -f pyproject.toml"
            timeout: PT5S
          unit:
            command: "python -c 'import src; print(OK)'"
            timeout: PT30S
        rollback: "rm -rf src/ pyproject.toml"

dependency_graph:
  T0.1:
    depends_on: []
  T0.2:
    depends_on: [T0.1]
    input_bindings:
      root: T0.1.output.project_root
```

### Task Block Delimiters (P2)

For markdown format, use explicit delimiters:

```markdown
<!-- TASK_BEGIN: T0.1 -->
```yaml
task_id: T0.1
name: "Setup project structure"
...
```
<!-- TASK_END: T0.1 -->
```

---

## Validation Rules

A Blueprint is **valid** if:

### Structural Validation
1. ✅ All task_ids are unique
2. ✅ All dependency references exist
3. ✅ No circular dependencies
4. ✅ All required fields present
5. ✅ Metadata block present (v2.0 mandatory)

### Interface Validation (P1)
6. ✅ All `output_port` references exist on source tasks
7. ✅ Input/output schemas are compatible where provided
8. ✅ Required bindings have reachable sources

### Execution Validation
9. ✅ All test_commands are non-empty and non-trivial
10. ✅ All rollback commands are non-empty
11. ✅ Status values are valid enum values
12. ✅ Duration fields use ISO 8601 PT format
13. ✅ Shell specification is valid

### Security Validation
14. ✅ Secret references use correct format (`${secrets.NAME}`)
15. ✅ No actual secrets appear in document
16. ✅ All secret references have resolution policy

### Preflight Validation
17. ✅ Preflight checks pass before execution
18. ✅ Required capabilities available
19. ✅ Resource locks are satisfiable

---

## Complete Example Task Block (v2.0)

```yaml
task_id: T1.2
name: "Implement JWT token validation"
status: not_started
assignee: null
estimated_sessions: 2
dependencies: [T1.1]

# NEW v2.0: Input bindings
input_bindings:
  jwt_config:
    source: T1.1
    output_port: jwt_config
    transfer: memory
    required: true
  secret_key:
    source: T0.1
    output_port: signing_key
    transfer: file
    required: true

interface:
  input: "JWT token string and secret key"
  input_type: json
  input_schema:
    type: object
    properties:
      token: { type: string, pattern: "^eyJ" }
      secret: { type: string, minLength: 32 }
    required: [token, secret]
  example_input: '{"token": "eyJhbGciOiJIUzI1NiIs...", "secret": "my-32-char-secret-key-here-now"}'

  output: "Validated claims or error"
  output_type: json
  output_schema:
    type: object
    properties:
      valid: { type: boolean }
      claims:
        type: object
        properties:
          user_id: { type: string }
          exp: { type: integer }
      error: { type: string }
    required: [valid]
  example_output: '{"valid": true, "claims": {"user_id": "u123", "exp": 1704326400}}'

# NEW v2.0: Output persistence
output:
  location: file
  path: "/tmp/blueprint/T1.2/output.json"
  format: json
  ports:
    validation_result:
      type: json
      schema:
        type: object
        properties:
          valid: { type: boolean }
    claims:
      type: json

# NEW v2.0: Required capabilities
required_capabilities:
  - python3.11
  - pyjwt

# NEW v2.0: Resources
resources:
  cpu: 1
  memory: "512Mi"
  timeout: PT5M
  locks: []

execution_context:
  working_directory: "/project"
  environment_variables:
    PYTHONPATH: "/project/src"
    JWT_SECRET: "${secrets.JWT_SECRET}"
  required_tools: [python3, pytest]
  setup_command: "pip install pyjwt pytest"

files_to_create:
  - src/auth/jwt.py
  - tests/test_jwt.py

acceptance_criteria:
  - "Validates JWT signature using HS256 algorithm"
  - "Rejects tokens where exp < current timestamp"
  - "Returns claims dict on valid token"
  - "Returns error message on invalid token"

# NEW v2.0: Tiered verification
verification:
  smoke:
    command: "python -c 'from src.auth.jwt import validate_token; print(\"OK\")'"
    timeout: PT10S
  unit:
    command: "cd /project && python -m pytest tests/test_jwt.py -v --tb=short"
    timeout: PT2M
  integration:
    command: "cd /project && python -m pytest tests/integration/test_auth.py -v"
    timeout: PT5M
    optional: true

# Legacy support
test_command: "cd /project && python -m pytest tests/test_jwt.py -v --tb=short"

# NEW v2.0: Hand-off protocol
handoff:
  checkpoint_format: json
  checkpoint_path: "/tmp/blueprint/T1.2/checkpoint.json"
  resume_strategy: from_checkpoint
  state_fields:
    - files_created
    - tests_passed
  on_interrupt:
    action: checkpoint
    timeout: PT10S

on_failure:
  max_retries: 2
  retry_delay: PT10S
  action: block

rollback: "git checkout HEAD~1 -- src/auth/jwt.py tests/test_jwt.py"

notes: "Use PyJWT library. HS256 algorithm. Claims must include user_id and exp."
```

---

## File Format

- **Extension**: `.md` (Markdown), `.bp.md` (Blueprint-specific), `.bp.yaml` (canonical)
- **Encoding**: UTF-8
- **YAML blocks**: Fenced with triple backticks and `yaml` language tag
- **Duration format**: ISO 8601 (e.g., `PT1H`, `PT30M`, `PT10S`)

---

## Migration from v1.x

v2.0 introduces **breaking changes** for multi-agent execution support.

### Breaking Changes

| Change | v1.x | v2.0 |
|--------|------|------|
| Output persistence | Implicit | Explicit `output` block required |
| Dependencies | Task ID list | Typed with `input_bindings` |
| Timeout format | `timeout_seconds: 3600` | `timeout: PT1H` (ISO 8601) |
| Retry delay | `retry_delay_seconds: 5` | `retry_delay: PT5S` (ISO 8601) |
| Secret handling | Undefined on missing | Explicit `on_missing` policy |

### Migration Steps

1. **Add output blocks** to all tasks that produce data
2. **Convert dependencies** to typed `input_bindings`
3. **Update duration fields** to ISO 8601 PT format
4. **Add secret resolution policy** to execution config
5. **Add preflight_checks** for required tools
6. **Update metadata** to v2.0.0

### Backward Compatibility (v2.0.1 Clarification)

**Strict Mode (default):** v2.0 enforces all required fields. Validation fails without `output` block.

**Migration Mode (opt-in):** For gradual migration, executors MAY support legacy mode via configuration flag:

```yaml
execution:
  compatibility_mode: v1_migration    # Enable v1.x compatibility shims
```

When `compatibility_mode: v1_migration` is set:
- Parser accepts v1.x `timeout_seconds` and converts to ISO 8601
- Missing `output` block → auto-generate with `location: stdout`
- Missing `input_bindings` → infer from `dependencies` list

**Important:** Migration mode is for transitional use only. New Blueprints MUST use v2.0 syntax.

| Mode | output required | input_bindings required | Recommended |
|------|-----------------|------------------------|-------------|
| Strict (default) | Yes | Yes | ✅ New projects |
| v1_migration | No (defaults to stdout) | No (inferred) | ⚠️ Migration only |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-01-03 | Initial draft specification |
| 1.3.0 | 2026-01-04 | Added: execution_context, typed interfaces, error policy |
| 1.4.0 | 2026-01-05 | Metadata block mandatory |
| **2.0.0** | 2026-01-05 | **Universal AI Orchestration Contract**: output persistence, hand-off protocol, data transfer mechanisms, secret resolution, interface satisfiability, parallelization controls, tiered verification, preflight checks, ISO 8601 durations |

---

## Appendix A: Priority Classification

Fleet consensus identified issues by severity:

### P0 — Blocks Multi-Agent Execution
- ✅ Output persistence mechanism
- ✅ Hand-off protocol (checkpoint/resume)
- ✅ Data transfer mechanism (stdout/file/memory/network)
- ✅ Secret resolution failure behavior

### P1 — Significantly Improves Reliability
- ✅ Interface satisfiability (schemas/key mapping)
- ✅ Parallelization controls (max_parallel, locks)
- ✅ Shell contract (explicit shell + flags)
- ✅ Duration format (ISO 8601)
- ✅ Version alignment (header/body)

### P2 — Format Improvements
- ✅ Task block delimiters
- ✅ Structured YAML dependency map
- ✅ Typed dependency references
- ✅ Canonical `.bp.yaml` format
- ✅ YAML frontmatter for metadata

---

## Appendix B: Path Variable Substitution (v2.0.1)

Blueprint supports variable substitution in path fields. Variables are replaced at execution time by the executor.

### Available Variables

| Variable | Scope | Description | Example Value |
|----------|-------|-------------|---------------|
| `${task_id}` | Task | Current task identifier | `T1.2` |
| `${blueprint_id}` | Document | Blueprint unique identifier | `bp-2026-01-05-001` |
| `${blueprint_root}` | Document | Root directory of Blueprint execution | `/project` |
| `${working_directory}` | Task | Task's working directory | `/project/src` |
| `${source_task_id}` | Binding | Source task for input binding | `T0.1` |
| `${output_port}` | Binding | Output port name being consumed | `config_path` |
| `${timestamp}` | Runtime | ISO 8601 timestamp | `2026-01-05T12:30:00Z` |
| `${timestamp_unix}` | Runtime | Unix epoch seconds | `1736080200` |
| `${executor_id}` | Runtime | Unique executor instance ID | `exec-abc123` |

### Secret Variables

Secret variables use a different namespace and are never logged:

| Variable | Description |
|----------|-------------|
| `${secrets.NAME}` | Secret value from resolution chain |
| `${secrets.NAME:default}` | Secret with default fallback |

### Escaping Rules

| Input | Output | Use Case |
|-------|--------|----------|
| `${task_id}` | Task ID value | Normal substitution |
| `$${task_id}` | `${task_id}` (literal) | Escape to preserve literal `${` |
| `\${task_id}` | `${task_id}` (literal) | Alternative escape syntax |

### Substitution Order

1. **Secrets** — Resolved first via `secret_resolution.sources` chain
2. **Document variables** — `blueprint_id`, `blueprint_root`
3. **Task variables** — `task_id`, `working_directory`
4. **Binding variables** — `source_task_id`, `output_port` (only in input_bindings)
5. **Runtime variables** — `timestamp`, `executor_id` (resolved at execution)

### Invalid Variable Behavior

| Scenario | Behavior |
|----------|----------|
| Unknown variable `${unknown}` | Preflight validation error |
| Unresolved secret `${secrets.MISSING}` | Per `secret_resolution.on_missing` policy |
| Circular reference | Preflight validation error |
| Malformed `${unclosed` | Preflight validation error |

### Examples

```yaml
# Task output path using task_id
output:
  path: "/tmp/blueprint/${task_id}/output.json"
  # Resolves to: /tmp/blueprint/T1.2/output.json

# Input binding with source context
input_bindings:
  config:
    source: T0.1
    fallback:
      path: "/tmp/blueprint/${source_task_id}/${output_port}.json"
      # Resolves to: /tmp/blueprint/T0.1/config_path.json

# Timestamp for unique artifacts
output:
  path: "/artifacts/${blueprint_id}/${task_id}/${timestamp_unix}.json"
  # Resolves to: /artifacts/bp-2026-01-05-001/T1.2/1736080200.json

# Escaped literal (not substituted)
notes: "Use $${task_id} in your command to reference the task"
# Resolves to: "Use ${task_id} in your command to reference the task"
```

---

## Appendix C: Executor Reference Implementation (v2.0.2)

This appendix provides guidance for implementing a compliant Blueprint executor.

### Minimum Viable Executor

A compliant executor MUST implement these core capabilities:

```yaml
executor_requirements:
  parsing:
    - Parse YAML task blocks from Markdown
    - Validate required fields (task_id, name, status, dependencies, interface, test_command, rollback)
    - Build dependency DAG

  validation:
    - Detect circular dependencies
    - Verify interface satisfiability
    - Check secret reference format
    - Validate status enum values

  execution:
    - Topological sort for execution order
    - Run test_command and interpret exit codes
    - Apply on_failure policy (retry, block, abort, skip)
    - Execute rollback on failure (if configured)

  state_management:
    - Track task status transitions
    - Persist checkpoints (if handoff configured)
    - Resume from checkpoint on restart
```

### Executor Lifecycle

```
┌─────────────┐
│   PARSE     │  Read Blueprint, extract task blocks
└──────┬──────┘
       ▼
┌─────────────┐
│  VALIDATE   │  Check schema, deps, interfaces
└──────┬──────┘
       ▼
┌─────────────┐
│   PLAN      │  Topological sort, identify parallelism
└──────┬──────┘
       ▼
┌─────────────┐
│  EXECUTE    │  Run tasks, handle failures, checkpoint
└──────┬──────┘
       ▼
┌─────────────┐
│  REPORT     │  Emit structured results, update status
└─────────────┘
```

### Required Behaviors

| Behavior | Requirement |
|----------|-------------|
| Dependency resolution | Execute only when ALL dependencies are `complete` |
| Failure handling | Apply `on_failure` policy before marking `blocked` |
| Status persistence | Write status changes atomically |
| Secret handling | NEVER log or expose secret values |
| Timeout enforcement | Kill tasks exceeding `timeout_seconds` |
| Rollback execution | Run rollback in reverse dependency order |

### Reference Implementation Structure

```
executor/
├── parser/
│   ├── markdown.py      # Extract YAML blocks from .md
│   ├── schema.py        # Validate against JSON Schema
│   └── dag.py           # Build dependency graph
├── validator/
│   ├── deps.py          # Circular dependency detection
│   ├── interface.py     # Interface satisfiability
│   └── secrets.py       # Secret reference validation
├── runtime/
│   ├── scheduler.py     # Topological sort, parallelism
│   ├── runner.py        # Task execution, test_command
│   ├── retry.py         # on_failure policy implementation
│   └── rollback.py      # Rollback orchestration
├── state/
│   ├── checkpoint.py    # Checkpoint persistence
│   ├── status.py        # Status transition management
│   └── resume.py        # Resume from checkpoint
└── reporter/
    ├── json.py          # Structured JSON output
    └── log.py           # Logging per specification
```

### Compliance Checklist

- [ ] Parses all v2.0 required fields
- [ ] Validates dependency DAG (no cycles)
- [ ] Respects `max_parallel` limits
- [ ] Applies resource lock precedence correctly
- [ ] Implements all `on_failure` actions
- [ ] Persists checkpoints atomically
- [ ] Resumes from checkpoints correctly
- [ ] Emits structured error messages per schema
- [ ] Logs in specified format (json/text/ndjson)
- [ ] Handles all status transitions per state machine

---

## Appendix D: Platform Assumptions (v2.0.2)

The Blueprint specification makes certain platform assumptions. This appendix documents these assumptions and provides guidance for cross-platform implementations.

### Default Target Platform

The specification is **primarily designed for Unix-like systems** (Linux, macOS, BSD).

### Assumptions Made

| Assumption | Impact | Cross-Platform Note |
|------------|--------|---------------------|
| Forward slash paths (`/`) | `working_directory`, `files_to_create` | Windows executors MUST normalize to native separators |
| Shell syntax (`\|`, `&&`, `;`) | `test_command`, `setup_command`, `rollback` | Use `/bin/sh` on Unix, `cmd /c` or PowerShell on Windows |
| Environment variable syntax (`$VAR`) | Commands, `${secrets.X}` | Works on both, but Windows uses `%VAR%` natively |
| Exit code 0 = success | `test_command` verification | Universal convention |
| `/tmp` temporary directory | Implicit temp file usage | Use platform temp directory API |
| Case-sensitive filesystem | File path matching | Windows is case-insensitive by default |

### Path Handling Rules

```yaml
# Blueprint paths use forward slashes (canonical format)
working_directory: "/project/src"
files_to_create:
  - "src/auth/jwt.py"
  - "tests/test_jwt.py"

# Executor responsibility: normalize for target platform
# Unix:    /project/src, src/auth/jwt.py
# Windows: C:\project\src, src\auth\jwt.py
```

**Executor Requirements:**
1. Accept forward-slash paths in Blueprint
2. Normalize to native separator for file operations
3. Return forward-slash paths in output (for portability)

### Shell Command Execution

| Platform | Default Shell | Override |
|----------|---------------|----------|
| Linux | `/bin/sh` | `execution_context.shell` |
| macOS | `/bin/sh` | `execution_context.shell` |
| Windows | `cmd.exe` | `execution_context.shell` |

**Extended execution_context field (optional):**

```yaml
execution_context:
  shell: "/bin/bash"           # Explicit shell override
  shell_args: ["-e", "-o", "pipefail"]  # Shell arguments
```

### Cross-Platform Best Practices

1. **Avoid shell-specific syntax** in `test_command` when possible
2. **Use `python -c` or `node -e`** for portable one-liners
3. **Specify explicit shell** if Bash features required
4. **Test Blueprints on target platform** before deployment

### Platform Declaration (Optional)

Blueprints MAY declare target platform requirements:

```yaml
metadata:
  target_platform: linux    # linux | macos | windows | any
  min_os_version: "20.04"   # Platform-specific version
```

**Executor Behavior:**
- If `target_platform` specified and doesn't match, executor MAY:
  - Warn and proceed (best effort)
  - Abort with clear error (strict mode)
- If `any` or unspecified, executor attempts best-effort execution

---

## Appendix E: Storage Assumptions (v2.0.2)

The Blueprint specification assumes certain storage capabilities. This appendix documents these assumptions and provides guidance for distributed and cloud-native implementations.

### Default Storage Model

The specification **assumes shared filesystem access** between tasks by default.

### Assumptions Made

| Assumption | Impact | Alternative |
|------------|--------|-------------|
| Shared filesystem | Output artifacts accessible to dependent tasks | Object storage with signed URLs |
| Local file paths | `output.path`, `files_to_create` | URI scheme support |
| Atomic file writes | Checkpoint persistence | Distributed lock or CAS |
| File locking | Concurrent access prevention | Distributed coordination service |
| Disk space availability | Output artifact storage | Quota management, TTL cleanup |

### Storage Modes

Executors MAY support multiple storage backends:

```yaml
execution:
  storage:
    mode: shared_fs    # shared_fs | object_store | hybrid

    # For shared_fs mode
    shared_path: "/mnt/blueprints"

    # For object_store mode
    backend: s3
    bucket: "blueprint-artifacts"
    region: "us-east-1"
    prefix: "${blueprint_id}/"

    # For hybrid mode
    checkpoint_storage: object_store
    artifact_storage: shared_fs
```

### Storage Mode Behaviors

| Mode | Checkpoint Storage | Artifact Passing | Use Case |
|------|-------------------|------------------|----------|
| `shared_fs` | Local file | Direct path reference | Single-node, local dev |
| `object_store` | S3/GCS/Azure | Signed URLs | Distributed, cloud-native |
| `hybrid` | Object store | Shared filesystem | Multi-agent with persistent state |

### Artifact Reference Resolution

When storage mode is `object_store`, output paths are translated:

```yaml
# Blueprint declares (platform-agnostic)
output:
  path: "${blueprint_root}/artifacts/${task_id}/result.json"

# Executor resolves for object_store mode
# s3://blueprint-artifacts/bp-123/artifacts/T1.1/result.json

# Downstream task receives
input_bindings:
  T1.1.output:
    uri: "s3://blueprint-artifacts/bp-123/artifacts/T1.1/result.json"
    signed_url: "https://..."  # Time-limited access
    expires_at: "2026-01-05T15:00:00Z"
```

### Distributed Executor Requirements

For executors running tasks across multiple nodes:

1. **Checkpoint synchronization**: Use distributed-safe storage for checkpoints
2. **Artifact transfer**: Stage artifacts to shared storage before marking task complete
3. **Lock coordination**: Use distributed lock for concurrent modifications
4. **Failure recovery**: Handle partial artifact uploads on task failure

### Object Store Configuration

```yaml
execution:
  storage:
    mode: object_store
    backend: s3
    bucket: "blueprint-artifacts"
    region: "us-east-1"
    credentials:
      source: env    # env | iam_role | file
      # For env: reads AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
      # For iam_role: uses instance/pod role
      # For file: reads from credentials_file
    encryption:
      enabled: true
      kms_key_id: "${secrets.KMS_KEY_ID}"
    versioning: true   # Enable for checkpoint history
```

### Cross-Node Artifact Protocol

```
┌──────────────┐       ┌─────────────────┐       ┌──────────────┐
│   Task A     │       │  Object Store   │       │   Task B     │
│  (Node 1)    │       │    (S3/GCS)     │       │  (Node 2)    │
└──────┬───────┘       └────────┬────────┘       └──────┬───────┘
       │                        │                        │
       │  1. Upload artifact    │                        │
       │───────────────────────>│                        │
       │                        │                        │
       │  2. Mark complete      │                        │
       │───────────────────────>│                        │
       │                        │                        │
       │                        │  3. Get signed URL     │
       │                        │<───────────────────────│
       │                        │                        │
       │                        │  4. Download artifact  │
       │                        │<───────────────────────│
       │                        │                        │
```

**Default:** `mode: shared_fs` (backward compatible with v1.x Blueprints)

---

## Appendix F: JSON Schema

The complete JSON Schema for v2.0 validation is available at:
`schema/blueprint_schema_v2.0.0.json`

---

*Blueprint Standard Format v2.0.2*
*"Universal AI Orchestration Contract"*
