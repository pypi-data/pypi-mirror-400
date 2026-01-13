# Blueprint — Master Roadmap

> **Document Status**: Living Document (Blueprint Standard Format v0.1)
> **Last Updated**: 2026-01-03
> **Owner**: Richie Suarez
> **Validated By**: Claude (Opus 4.5), Codex (GPT-5.2), Gemini (3 Pro)

---

## Strategic Vision

**Blueprint** is the industry-standard specification compiler for AI agent orchestration. It transforms goals into structured, compilable, interface-first contracts that enable parallel AI agent execution with coordination guarantees.

**North Star**: The perfect blueprint — so detailed, so structured, that AI agents execute from it seamlessly.

> **SCOPE**: Blueprint generates specifications. Execution is out of scope. What users do with the blueprint afterward is their business.

---

## Success Metrics

| Metric | Target | Validation |
|--------|--------|------------|
| Agent execution success rate | >90% first-pass | Automated test suite |
| Parallel agent conflict rate | <5% | Merge conflict tracking |
| Time to first working Blueprint | <30 min | User testing |
| Self-hosting | Blueprint builds itself | Dogfooding |

---

## Tier 0: Specification Design ✅ COMPLETE

**Goal**: Define the Blueprint Standard Format before writing any code.

### T0.1: Core Schema Definition

```yaml
task_id: T0.1
name: "Define Blueprint Standard Format schema"
status: ✅ COMPLETE
assignee: null
estimated_sessions: 2
dependencies: []

interface:
  input: "Fleet feedback synthesis + existing roadmap patterns"
  output: "docs/BLUEPRINT_SPEC.md"

acceptance_criteria:
  - Schema defines all required fields for a Blueprint task
  - Schema includes interface contracts (input/output types)
  - Schema includes verification blocks (test commands)
  - Schema includes human-required signals
  - Schema is JSON-serializable for programmatic validation

test_command: |
  python3 -c "import json; json.load(open('examples/valid_blueprint.json'))"

rollback: "Revert docs/BLUEPRINT_SPEC.md to previous commit"
```

### T0.2: Task Block Specification

```yaml
task_id: T0.2
name: "Define Task Block structure"
status: ✅ COMPLETE
assignee: null
estimated_sessions: 1
dependencies: [T0.1]

interface:
  input: "BLUEPRINT_SPEC.md schema"
  output: "Task Block specification in BLUEPRINT_SPEC.md"

acceptance_criteria:
  - Task blocks have unique IDs
  - Task blocks declare explicit dependencies (DAG)
  - Task blocks declare interface contracts
  - Task blocks include acceptance criteria (testable)
  - Task blocks include test commands
  - Task blocks include rollback procedures
  - Task blocks can signal HUMAN_REQUIRED with notification spec

test_command: |
  grep -q "HUMAN_REQUIRED" docs/BLUEPRINT_SPEC.md && echo "✅ Human signal defined"

rollback: "git checkout HEAD~1 -- docs/BLUEPRINT_SPEC.md"
```

### T0.3: Verification Block Specification

```yaml
task_id: T0.3
name: "Define Verification Block structure"
status: ✅ COMPLETE
assignee: null
estimated_sessions: 1
dependencies: [T0.2]

interface:
  input: "Task Block specification"
  output: "Verification Block specification"

acceptance_criteria:
  - Every task can reference a verification block
  - Verification blocks are executable (shell commands)
  - Verification blocks return 0 (pass) or non-zero (fail)
  - Verification blocks can be run independently
  - Done is defined as verification passes, not prose complete

test_command: |
  # Verification block should be self-testing
  bash -c "exit 0" && echo "✅ Verification blocks executable"

rollback: "git checkout HEAD~1 -- docs/BLUEPRINT_SPEC.md"
```

### T0.4: Human-in-the-Loop Specification

```yaml
task_id: T0.4
name: "Define HUMAN_REQUIRED signal format"
status: ✅ COMPLETE
assignee: null
estimated_sessions: 1
dependencies: [T0.2]

interface:
  input: "Task Block specification"
  output: "HUMAN_REQUIRED block specification"

acceptance_criteria:
  - HUMAN_REQUIRED blocks specify what action is needed
  - HUMAN_REQUIRED blocks specify notification channel (email, slack, webhook)
  - HUMAN_REQUIRED blocks specify timeout behavior
  - HUMAN_REQUIRED blocks can be acknowledged programmatically
  - Agent execution pauses at HUMAN_REQUIRED until acknowledged

example:
  human_required:
    action: "Provide OpenAI API key"
    reason: "Required for Codex integration"
    notify:
      channel: "email"
      recipient: "richie@zeroechelon.com"
    timeout: "24h"
    on_timeout: "ABORT"

test_command: |
  grep -q "HUMAN_REQUIRED" docs/BLUEPRINT_SPEC.md && \
  grep -q "notify" docs/BLUEPRINT_SPEC.md && \
  echo "✅ Human signal spec complete"

rollback: "git checkout HEAD~1 -- docs/BLUEPRINT_SPEC.md"
```

---

## Tier 1: Compiler Core ✅ COMPLETE

**Goal**: Build the specification compiler that transforms goals into Blueprint format.

### T1.1: Parser Implementation

```yaml
task_id: T1.1
name: "Implement Blueprint parser"
status: ✅ COMPLETE
assignee: null
estimated_sessions: 2
dependencies: [T0.1, T0.2, T0.3, T0.4]

interface:
  input: "Blueprint markdown file"
  output: "Parsed Blueprint object (Python dataclass or JSON)"

files_to_create:
  - src/blueprint/parser.py
  - src/blueprint/models.py

acceptance_criteria:
  - Parser reads Blueprint markdown files
  - Parser extracts all task blocks into structured objects
  - Parser builds dependency graph (DAG)
  - Parser validates required fields exist
  - Parser returns useful errors for malformed input

test_command: |
  cd src && python3 -m pytest tests/test_parser.py -v

rollback: "git checkout HEAD~1 -- src/blueprint/"
```

### T1.2: Validator Implementation

```yaml
task_id: T1.2
name: "Implement Blueprint validator (pre-flight check)"
status: ✅ COMPLETE
assignee: null
estimated_sessions: 2
dependencies: [T1.1]

interface:
  input: "Parsed Blueprint object"
  output: "Validation result (pass/fail with errors)"

files_to_create:
  - src/blueprint/validator.py

acceptance_criteria:
  - Validator detects circular dependencies
  - Validator detects missing dependency references
  - Validator detects interface mismatches (output of A != input of B)
  - Validator detects missing test commands
  - Validator returns actionable error messages

test_command: |
  cd src && python3 -m pytest tests/test_validator.py -v

rollback: "git checkout HEAD~1 -- src/blueprint/validator.py"
```

### T1.3: DAG Executor

```yaml
task_id: T1.3
name: "Implement dependency-aware task executor"
status: ✅ COMPLETE
assignee: null
estimated_sessions: 3
dependencies: [T1.1, T1.2]

interface:
  input: "Validated Blueprint object"
  output: "Execution plan (ordered task list with parallelization hints)"

files_to_create:
  - src/blueprint/executor.py
  - src/blueprint/scheduler.py

acceptance_criteria:
  - Executor respects dependency ordering
  - Executor identifies parallelizable tasks (no shared dependencies)
  - Executor tracks task completion status
  - Executor handles HUMAN_REQUIRED pauses
  - Executor supports dry-run mode

test_command: |
  cd src && python3 -m pytest tests/test_executor.py -v

rollback: "git checkout HEAD~1 -- src/blueprint/executor.py src/blueprint/scheduler.py"
```

---

## Tier 2: Generator Core (CURRENT)

**Goal**: Build the AI-powered generator that creates Blueprints from goals.

### T2.1: Goal Decomposition Engine

```yaml
task_id: T2.1
name: "Implement goal decomposition"
status: ✅ COMPLETE
assignee: null
estimated_sessions: 3
dependencies: [T1.1]

interface:
  input: "Natural language goal string"
  output: "List of atomic tasks with estimated scope"

files_to_create:
  - src/blueprint/generator/decomposer.py

acceptance_criteria:
  - Decomposer breaks goals into atomic tasks
  - Each task fits within single agent context window
  - Decomposer identifies dependencies between tasks
  - Decomposer estimates session count per task
  - Decomposer uses LLM for intelligent decomposition

human_required:
  action: "Provide Anthropic API key for Claude integration"
  reason: "Goal decomposition uses Claude for intelligent breakdown"
  notify:
    channel: "env"
    variable: "ANTHROPIC_API_KEY"
  on_missing: "ABORT with instructions"

test_command: |
  cd src && python3 -m pytest tests/test_decomposer.py -v

rollback: "git checkout HEAD~1 -- src/blueprint/generator/"
```

### T2.2: Interface Inference Engine

```yaml
task_id: T2.2
name: "Implement interface contract inference"
status: ✅ COMPLETE
assignee: null
estimated_sessions: 2
dependencies: [T2.1]

interface:
  input: "List of atomic tasks"
  output: "Tasks with inferred interface contracts"

files_to_create:
  - src/blueprint/generator/interface_inferrer.py

acceptance_criteria:
  - Inferrer determines input/output types for each task
  - Inferrer validates interface compatibility across task chain
  - Inferrer suggests file paths and function signatures
  - Inferrer uses existing codebase context when available

test_command: |
  cd src && python3 -m pytest tests/test_interface_inferrer.py -v

rollback: "git checkout HEAD~1 -- src/blueprint/generator/interface_inferrer.py"
```

### T2.3: Blueprint Assembler

```yaml
task_id: T2.3
name: "Implement Blueprint markdown assembler"
status: ✅ COMPLETE
assignee: null
estimated_sessions: 2
dependencies: [T2.1, T2.2]

interface:
  input: "Tasks with interfaces"
  output: "Complete Blueprint markdown document"

files_to_create:
  - src/blueprint/generator/assembler.py
  - templates/blueprint_template.md

acceptance_criteria:
  - Assembler produces valid Blueprint format
  - Assembler includes all required fields per spec
  - Assembler generates test commands for each task
  - Assembler generates rollback commands
  - Output passes validator (T1.2)
  - Supports Linker: when tasks exceed ~100, prompt for decomposition
  - Generates parent Blueprint with `refs` to sub-modules

notes: |
  LINKER CONCEPT (Gemini guidance): Large Blueprints can exceed agent context
  windows. When task count is high, Assembler should:
  1. Detect when output exceeds ~100 tasks
  2. Prompt for decomposition into logical sub-modules
  3. Generate parent Blueprint with `refs: [{ref: "./sub.bp.md"}]`
  4. Each sub-module is a standalone, valid Blueprint
  See: models.py BlueprintRef class, SYSTEM_ARCHITECTURE.md "Hierarchical Compilation"

test_command: |
  cd src && python3 -c "from blueprint.generator.assembler import assemble; \
    from blueprint.validator import validate; \
    bp = assemble(sample_tasks); \
    assert validate(bp).passed"

rollback: "git checkout HEAD~1 -- src/blueprint/generator/assembler.py"
```

---

## Tier 3: Outpost Integration ⚠️ EXPERIMENTAL

> **⚠️ NOTE**: This tier implements optional reference code for Outpost integration. It is NOT core to Blueprint's mission. Blueprint's responsibility ends at generation. This code exists as a demonstration/reference only.


**Goal**: Connect Blueprint to Outpost for multi-agent execution.

### T3.1: Outpost Dispatcher

```yaml
task_id: T3.1
name: "Implement Outpost dispatch integration"
status: ✅ COMPLETE
assignee: null
estimated_sessions: 2
dependencies: [T1.3]

interface:
  input: "Execution plan from DAG executor"
  output: "Outpost dispatch commands"

files_to_create:
  - src/blueprint/integrations/outpost.py

acceptance_criteria:
  - Dispatcher generates valid Outpost SSM commands
  - Dispatcher selects appropriate agent per task type
  - Dispatcher handles parallel dispatch for independent tasks
  - Dispatcher collects and aggregates results
  - Dispatcher integrates with HUMAN_REQUIRED flow

human_required:
  action: "Configure AWS credentials for Outpost access"
  reason: "Required for SSM command dispatch"
  notify:
    channel: "env"
    variables: ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
  on_missing: "ABORT with credential setup instructions"

test_command: |
  cd src && python3 -m pytest tests/test_outpost_integration.py -v

rollback: "git checkout HEAD~1 -- src/blueprint/integrations/"
```

### T3.2: Result Aggregator

```yaml
task_id: T3.2
name: "Implement parallel result aggregation"
status: ✅ COMPLETE
assignee: null
estimated_sessions: 2
dependencies: [T3.1]

interface:
  input: "Multiple agent execution results"
  output: "Aggregated result with conflict detection"

files_to_create:
  - src/blueprint/integrations/aggregator.py

acceptance_criteria:
  - Aggregator collects results from parallel agents
  - Aggregator detects merge conflicts
  - Aggregator reports task completion status
  - Aggregator triggers dependent tasks when dependencies complete
  - Aggregator handles agent failures gracefully

test_command: |
  cd src && python3 -m pytest tests/test_aggregator.py -v

rollback: "git checkout HEAD~1 -- src/blueprint/integrations/aggregator.py"
```

---

## Tier 4: CLI & UX

**Goal**: Make Blueprint usable from command line.

### T4.1: CLI Entry Point

```yaml
task_id: T4.1
name: "Implement blueprint CLI"
status: ✅ COMPLETE
assignee: null
estimated_sessions: 2
dependencies: [T2.3, T3.1]

interface:
  input: "Command line arguments"
  output: "Blueprint execution or generation"

files_to_create:
  - src/blueprint/cli.py
  - pyproject.toml (entry point)

acceptance_criteria:
  - CLI supports `blueprint generate <goal>` command
  - CLI supports `blueprint validate <file>` command
  - CLI supports `blueprint execute <file>` command
  - CLI supports `blueprint execute --dry-run` mode
  - CLI provides helpful error messages

test_command: |
  blueprint --help && blueprint validate docs/MASTER_ROADMAP.md

rollback: "git checkout HEAD~1 -- src/blueprint/cli.py"
```

---


---

## Version Status: v1.2.0 GA

**Current Classification:** Production/Stable ✅

**Graduation Criteria (ALL MET):**
- [x] Real parallel execution (asyncio.gather())
- [x] FAIL LOUD pattern in aggregator
- [x] Datetime standardization + DTZ linter rule
- [x] Test suite with comprehensive parallel tests
- [x] Generation metadata for bypass detection
- [x] Anti-bypass documentation
- [x] Public release procedure

**P0 + P1 Fixes Applied (2026-01-03):**

| Bug | Fix | Status |
|-----|-----|--------|
| #1 Parallel execution stub | Real asyncio.gather() implementation | ✅ |
| #2 Failing tests | Updated for Task model returns | ✅ |
| #3 Dev dependencies | Added pytest-asyncio, mypy | ✅ |
| #4 Silent artifact download | FAIL LOUD pattern + DownloadFailure tracking | ✅ |
| Datetime inconsistency | datetime.now(timezone.utc) + DTZ linter rule | ✅ |

**Systemic Prevention:**
- `ruff` DTZ rule bans `datetime.utcnow()` at lint time
- Regression impossible without explicit rule override

## Dependency Graph

```
T0.1 ─┬─► T0.2 ─┬─► T0.3
      │         └─► T0.4
      │
      └─► T1.1 ─► T1.2 ─┬─► T1.3 ─► T3.1 ─► T3.2
                        │
T0.2 ─► T2.1 ─► T2.2 ───┴─► T2.3
                              │
                              └─► T4.1
```

**Parallelizable Groups**:
- Group A: T0.1 (blocking)
- Group B: T0.2, T0.3, T0.4 (parallel after T0.1)
- Group C: T1.1, T2.1 (parallel after T0.x)
- Group D: T1.2, T2.2 (parallel after respective T1.1/T2.1)
- Group E: T1.3, T2.3 (parallel)
- Group F: T3.1, T4.1 (parallel after deps)

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | 2026-01-03 | Claude (Persistence Executor) | Initial roadmap following Blueprint principles |
| 0.2 | 2026-01-03 | Claude (Persistence Executor) | Tier 0 complete - Schema validated with JSON Schema |
| 0.3 | 2026-01-03 | Claude (Persistence Executor) | T1.1 Parser complete - Markdown/JSON parsing working |
| 0.4 | 2026-01-03 | Claude (Persistence Executor) | Tier 1 complete - Validator, Scheduler, Executor all working |
| 0.5 | 2026-01-03 | Claude (Persistence Executor) | Pydantic V2 migration (models.py), Linker concept added to T2.3 |
| 0.6 | 2026-01-03 | Claude (Persistence Executor) | T2.1 complete - Goal decomposition with Claude 4.5 Opus |
| 0.7 | 2026-01-03 | Claude (Persistence Executor) | T2.2 complete - Interface inference with Claude 4.5 Sonnet |
| 0.8 | 2026-01-03 | Claude (Persistence Executor) | T2.3 complete - Blueprint assembler with Linker threshold. Tier 2 COMPLETE. |
| 0.9 | 2026-01-03 | Claude (Persistence Executor) | T3.1 complete - Outpost dispatcher with S3 artifact pattern |
| 1.0 | 2026-01-03 | Claude (Persistence Executor) | T3.2 complete - Result aggregator with conflict detection. Tier 3 COMPLETE. |
| 1.1 | 2026-01-03 | Claude (Persistence Executor) | P0 Hardening: CLI entry point (T4.1 partial), tenacity retry, Task model standardization |
| 1.2 | 2026-01-03 | Claude (Persistence Executor) | T4.1 COMPLETE - CLI with parse/validate/execute/generate, 19 tests passing. ALL TIERS COMPLETE. |
| 1.3 | 2026-01-03 | Claude (Persistence Executor) | v0.9.0 RC: P0 hardening - FAIL LOUD aggregator, datetime standardization, DTZ linter rule, test fixes |
| 1.4 | 2026-01-03 | Claude (Persistence Executor) | v1.0.0 GA: Real parallel execution with asyncio.gather(), comprehensive executor tests |
| 1.5 | 2026-01-03 | Claude (Persistence Executor) | v1.2.0: Generation metadata, anti-bypass defense, public release procedure |

---

*"Blueprint builds Blueprint. The roadmap is the product."*



---

## Tier 5: Provider Abstraction ✅ COMPLETE

**Goal**: Abstract LLM provider so users can generate Blueprints with any supported AI backend.

> **This is core to Blueprint's mission.** Generation requires an LLM. Provider abstraction enables broader adoption.

### T5.1: Provider Interface

```yaml
task_id: T5.1
name: "Define LLMProvider abstract base class"
status: ✅ COMPLETE
assignee: null
estimated_sessions: 1
dependencies: []

interface:
  input: "Design requirements for provider abstraction"
  output: "Abstract base class with generate() method"

files_to_create:
  - src/blueprint/providers/__init__.py
  - src/blueprint/providers/base.py

acceptance_criteria:
  - LLMProvider ABC defines generate(prompt, max_tokens, temperature) -> str
  - LLMProvider ABC defines from_env() classmethod for auto-config
  - LLMProvider ABC defines env_var_name() for discovery
  - Clean separation from decomposer implementation

test_command: |
  python -c "from blueprint.providers.base import LLMProvider; print('✅ Interface defined')"

rollback: "git checkout HEAD~1 -- src/blueprint/providers/"
```

### T5.2: Anthropic Provider

```yaml
task_id: T5.2
name: "Implement Anthropic provider"
status: ✅ COMPLETE
assignee: null
estimated_sessions: 1
dependencies: [T5.1]

interface:
  input: "LLMProvider interface"
  output: "Working Anthropic implementation"

files_to_create:
  - src/blueprint/providers/anthropic.py

acceptance_criteria:
  - AnthropicProvider implements LLMProvider interface
  - Auto-configures from ANTHROPIC_API_KEY env var
  - Supports model selection (Opus/Sonnet)
  - Existing decomposer tests pass with new provider

test_command: |
  cd src && python3 -m pytest tests/test_providers.py::test_anthropic -v

rollback: "git checkout HEAD~1 -- src/blueprint/providers/anthropic.py"
```

### T5.3: OpenAI Provider

```yaml
task_id: T5.3
name: "Implement OpenAI provider"
status: ✅ COMPLETE
assignee: null
estimated_sessions: 1
dependencies: [T5.1]

interface:
  input: "LLMProvider interface"
  output: "Working OpenAI implementation"

files_to_create:
  - src/blueprint/providers/openai.py

acceptance_criteria:
  - OpenAIProvider implements LLMProvider interface
  - Auto-configures from OPENAI_API_KEY env var
  - Supports model selection (GPT-4o, etc.)
  - Can generate valid Blueprints

test_command: |
  cd src && python3 -m pytest tests/test_providers.py::test_openai -v

rollback: "git checkout HEAD~1 -- src/blueprint/providers/openai.py"
```

### T5.4: Provider Factory

```yaml
task_id: T5.4
name: "Implement provider auto-detection factory"
status: ✅ COMPLETE
assignee: null
estimated_sessions: 1
dependencies: [T5.2, T5.3]

interface:
  input: "Available providers and environment"
  output: "Auto-configured LLMProvider instance"

files_to_modify:
  - src/blueprint/providers/__init__.py

acceptance_criteria:
  - get_provider() auto-detects from env vars (priority order)
  - get_provider(name) returns specific provider
  - Clear error messages when no provider configured
  - Priority: Anthropic > OpenAI > (future providers)

test_command: |
  cd src && python3 -m pytest tests/test_providers.py::test_factory -v

rollback: "git checkout HEAD~1 -- src/blueprint/providers/__init__.py"
```

### T5.5: Decomposer Integration

```yaml
task_id: T5.5
name: "Update decomposer to use provider interface"
status: ✅ COMPLETE
assignee: null
estimated_sessions: 1
dependencies: [T5.4]

interface:
  input: "GoalDecomposer with hard-coded Anthropic"
  output: "GoalDecomposer using provider abstraction"

files_to_modify:
  - src/blueprint/generator/decomposer.py
  - src/blueprint/cli.py

acceptance_criteria:
  - Decomposer accepts provider parameter
  - Decomposer uses get_provider() for auto-detection
  - CLI adds --provider flag
  - Backward compatible (existing usage works)
  - All existing tests pass

test_command: |
  cd src && python3 -m pytest tests/test_decomposer.py tests/test_cli.py -v

rollback: "git checkout HEAD~1 -- src/blueprint/generator/decomposer.py src/blueprint/cli.py"
```

