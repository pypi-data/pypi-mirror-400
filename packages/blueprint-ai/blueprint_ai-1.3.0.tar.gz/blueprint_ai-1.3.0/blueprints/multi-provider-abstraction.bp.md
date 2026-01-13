# Multi-Provider Abstraction Layer — Implementation Blueprint

> **Document Status**: Draft
> **Last Updated**: 2026-01-05
> **Owner**: Blueprint Team

<!-- BLUEPRINT METADATA (DO NOT REMOVE) -->
<!-- _blueprint_version: 2.0.2 -->
<!-- _generated_at: 2026-01-05T13:30:00Z -->
<!-- _generator: claude-opus-4.5 -->
<!-- END METADATA -->

---

## Strategic Vision

Implement an optional, backwards-compatible multi-provider abstraction layer in Blueprint's Python API. This enables users to choose between Anthropic (default), OpenAI, Google, and other LLM providers for goal decomposition without altering the core Blueprint spec or breaking existing workflows.

**Fleet Consensus Summary:**
- Spec v2.0.2 remains frozen (4/4 agreement)
- Add optional provider abstraction (3/4 favor)
- Provider registry pattern with pluggable clients
- Backwards-compatible defaults (Anthropic continues to work unchanged)

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Backwards compatibility | 100% | Existing code with `ANTHROPIC_API_KEY` works unchanged |
| Provider coverage | 4 providers | Anthropic, OpenAI, Google, Outpost |
| Configuration overhead | Minimal | Single env var or config option |
| Test coverage | 90%+ | Unit tests for each provider adapter |

---

## Execution Configuration

```yaml
execution:
  shell: bash
  shell_flags: ["-e", "-o", "pipefail"]
  max_parallel_tasks: 2
  preflight_checks:
    - command: "python3 --version"
      expected_exit_code: 0
      error_message: "Python 3.11+ required"
    - command: "test -d src/blueprint"
      expected_exit_code: 0
      error_message: "Blueprint source directory must exist"
```

---

## Tier 0: Foundation

### T0.1: Define Provider Interface

```yaml
task_id: T0.1
name: "Define abstract provider interface"
status: not_started
dependencies: []

interface:
  input: "Blueprint spec v2.0.2 requirements, decomposer.py analysis"
  output: "Abstract base class for LLM providers"

input_bindings: {}

output:
  location: file
  path: "src/blueprint/providers/base.py"
  ports:
    provider_interface:
      type: file_path

required_capabilities:
  - python3.11

acceptance_criteria:
  - "ProviderBase ABC defined with abstract methods"
  - "Methods: generate_completion(prompt, max_tokens, **kwargs) -> str"
  - "Methods: get_model_name() -> str"
  - "Methods: validate_credentials() -> bool"
  - "Type hints for all methods"
  - "Docstrings with usage examples"

verification:
  smoke:
    command: "python -c 'from blueprint.providers.base import ProviderBase'"
    timeout: PT10S
  unit:
    command: "python -m pytest tests/providers/test_base.py -v"
    timeout: PT1M

rollback: "git checkout HEAD -- src/blueprint/providers/"

files_to_create:
  - src/blueprint/providers/__init__.py
  - src/blueprint/providers/base.py
  - tests/providers/__init__.py
  - tests/providers/test_base.py

notes: |
  Key design decisions:
  - Use ABC (abstract base class) pattern
  - Keep interface minimal to avoid leaky abstractions
  - Provider-specific features via **kwargs, not interface pollution
```

---

### T0.2: Implement Anthropic Provider

```yaml
task_id: T0.2
name: "Implement Anthropic provider adapter"
status: not_started
dependencies: [T0.1]

interface:
  input: "ProviderBase interface, existing Anthropic code from decomposer.py"
  output: "AnthropicProvider class implementing ProviderBase"

input_bindings:
  interface:
    source: T0.1
    output_port: provider_interface
    transfer: file
    required: true

output:
  location: file
  path: "src/blueprint/providers/anthropic.py"
  ports:
    anthropic_provider:
      type: file_path

required_capabilities:
  - python3.11
  - anthropic

acceptance_criteria:
  - "AnthropicProvider extends ProviderBase"
  - "Uses existing retry logic from decomposer.py"
  - "Supports claude-opus-4-5 and claude-sonnet-4-5 models"
  - "Reads ANTHROPIC_API_KEY from env if not provided"
  - "All existing decomposer.py tests pass with new provider"

verification:
  smoke:
    command: "python -c 'from blueprint.providers.anthropic import AnthropicProvider'"
    timeout: PT10S
  unit:
    command: "python -m pytest tests/providers/test_anthropic.py -v"
    timeout: PT2M

rollback: "git checkout HEAD -- src/blueprint/providers/anthropic.py"

files_to_create:
  - src/blueprint/providers/anthropic.py
  - tests/providers/test_anthropic.py

notes: |
  This is a refactor of existing code, not new functionality.
  Preserve all existing behavior exactly.
```

---

### T0.3: Implement Provider Registry

```yaml
task_id: T0.3
name: "Implement provider registry"
status: not_started
dependencies: [T0.1]

interface:
  input: "ProviderBase interface"
  output: "ProviderRegistry singleton with provider lookup"

input_bindings:
  interface:
    source: T0.1
    output_port: provider_interface
    transfer: file
    required: true

output:
  location: file
  path: "src/blueprint/providers/registry.py"
  ports:
    registry:
      type: file_path

required_capabilities:
  - python3.11

acceptance_criteria:
  - "ProviderRegistry class with singleton pattern"
  - "register(name, provider_class) method"
  - "get(name) -> ProviderBase method"
  - "list_providers() -> list[str] method"
  - "Default 'anthropic' provider auto-registered"
  - "Thread-safe registration"

verification:
  smoke:
    command: "python -c 'from blueprint.providers.registry import ProviderRegistry'"
    timeout: PT10S
  unit:
    command: "python -m pytest tests/providers/test_registry.py -v"
    timeout: PT1M

rollback: "git checkout HEAD -- src/blueprint/providers/registry.py"

files_to_create:
  - src/blueprint/providers/registry.py
  - tests/providers/test_registry.py

notes: |
  Registry pattern enables plugin-style provider addition.
  Users can register custom providers at runtime.
```

---

## Tier 1: Provider Implementations

### T1.1: Implement OpenAI Provider

```yaml
task_id: T1.1
name: "Implement OpenAI provider adapter"
status: not_started
dependencies: [T0.1, T0.3]

interface:
  input: "ProviderBase interface, OpenAI API documentation"
  output: "OpenAIProvider class implementing ProviderBase"

input_bindings:
  interface:
    source: T0.1
    output_port: provider_interface
    transfer: file
    required: true

output:
  location: file
  path: "src/blueprint/providers/openai.py"
  ports:
    openai_provider:
      type: file_path

required_capabilities:
  - python3.11
  - openai

acceptance_criteria:
  - "OpenAIProvider extends ProviderBase"
  - "Supports gpt-4, gpt-4-turbo, gpt-3.5-turbo models"
  - "Reads OPENAI_API_KEY from env if not provided"
  - "Handles OpenAI-specific error types"
  - "Auto-registered in ProviderRegistry"

verification:
  smoke:
    command: "python -c 'from blueprint.providers.openai import OpenAIProvider'"
    timeout: PT10S
  unit:
    command: "python -m pytest tests/providers/test_openai.py -v"
    timeout: PT2M

rollback: "git checkout HEAD -- src/blueprint/providers/openai.py"

files_to_create:
  - src/blueprint/providers/openai.py
  - tests/providers/test_openai.py

notes: |
  OpenAI dependency should be optional (extra install).
  Use try/except import pattern.
```

---

### T1.2: Implement Google Provider

```yaml
task_id: T1.2
name: "Implement Google Gemini provider adapter"
status: not_started
dependencies: [T0.1, T0.3]

interface:
  input: "ProviderBase interface, Google Generative AI documentation"
  output: "GoogleProvider class implementing ProviderBase"

input_bindings:
  interface:
    source: T0.1
    output_port: provider_interface
    transfer: file
    required: true

output:
  location: file
  path: "src/blueprint/providers/google.py"
  ports:
    google_provider:
      type: file_path

required_capabilities:
  - python3.11
  - google-generativeai

acceptance_criteria:
  - "GoogleProvider extends ProviderBase"
  - "Supports gemini-pro, gemini-1.5-pro models"
  - "Reads GOOGLE_API_KEY from env if not provided"
  - "Handles Google-specific error types"
  - "Auto-registered in ProviderRegistry"

verification:
  smoke:
    command: "python -c 'from blueprint.providers.google import GoogleProvider'"
    timeout: PT10S
  unit:
    command: "python -m pytest tests/providers/test_google.py -v"
    timeout: PT2M

rollback: "git checkout HEAD -- src/blueprint/providers/google.py"

files_to_create:
  - src/blueprint/providers/google.py
  - tests/providers/test_google.py

notes: |
  Google dependency should be optional (extra install).
  Use try/except import pattern.
```

---

### T1.3: Implement Outpost Provider

```yaml
task_id: T1.3
name: "Implement Outpost provider adapter"
status: not_started
dependencies: [T0.1, T0.3]

interface:
  input: "ProviderBase interface, Outpost dispatch system documentation"
  output: "OutpostProvider class implementing ProviderBase"

input_bindings:
  interface:
    source: T0.1
    output_port: provider_interface
    transfer: file
    required: true

output:
  location: file
  path: "src/blueprint/providers/outpost.py"
  ports:
    outpost_provider:
      type: file_path

required_capabilities:
  - python3.11

acceptance_criteria:
  - "OutpostProvider extends ProviderBase"
  - "Supports fleet dispatch via SSM"
  - "Reads OUTPOST_SSM_INSTANCE from env"
  - "No API key required (uses IAM role)"
  - "Can specify target agent (claude, codex, gemini, grok, aider)"
  - "Auto-registered in ProviderRegistry"

verification:
  smoke:
    command: "python -c 'from blueprint.providers.outpost import OutpostProvider'"
    timeout: PT10S
  unit:
    command: "python -m pytest tests/providers/test_outpost.py -v"
    timeout: PT2M

rollback: "git checkout HEAD -- src/blueprint/providers/outpost.py"

files_to_create:
  - src/blueprint/providers/outpost.py
  - tests/providers/test_outpost.py

notes: |
  This provider enables no-API-key usage via Outpost fleet.
  Requires AWS credentials with SSM access.
```

---

## Tier 2: Integration

### T2.1: Refactor GoalDecomposer to Use Provider Registry

```yaml
task_id: T2.1
name: "Refactor decomposer to use provider abstraction"
status: not_started
dependencies: [T0.2, T0.3]

interface:
  input: "ProviderRegistry, AnthropicProvider, existing decomposer.py"
  output: "Updated decomposer.py using provider abstraction"

input_bindings:
  registry:
    source: T0.3
    output_port: registry
    transfer: file
    required: true
  anthropic:
    source: T0.2
    output_port: anthropic_provider
    transfer: file
    required: true

output:
  location: file
  path: "src/blueprint/generator/decomposer.py"
  ports:
    decomposer:
      type: file_path

required_capabilities:
  - python3.11

acceptance_criteria:
  - "GoalDecomposer accepts provider parameter (default: 'anthropic')"
  - "Existing API unchanged (backwards compatible)"
  - "ANTHROPIC_API_KEY still works as before"
  - "New BLUEPRINT_PROVIDER env var for provider selection"
  - "All existing tests pass without modification"

verification:
  smoke:
    command: "python -c 'from blueprint.generator.decomposer import GoalDecomposer'"
    timeout: PT10S
  unit:
    command: "python -m pytest tests/generator/test_decomposer.py -v"
    timeout: PT2M
  integration:
    command: "python -m pytest tests/integration/test_provider_switching.py -v"
    timeout: PT5M
    optional: true

rollback: "git checkout HEAD -- src/blueprint/generator/decomposer.py"

files_to_modify:
  - src/blueprint/generator/decomposer.py

files_to_create:
  - tests/integration/test_provider_switching.py

notes: |
  CRITICAL: Must maintain 100% backwards compatibility.
  Default behavior must be identical to current implementation.
```

---

### T2.2: Update Package Configuration

```yaml
task_id: T2.2
name: "Update package extras for optional providers"
status: not_started
dependencies: [T1.1, T1.2, T1.3]

interface:
  input: "Provider implementations"
  output: "Updated pyproject.toml with optional dependencies"

input_bindings: {}

output:
  location: file
  path: "pyproject.toml"
  ports:
    config:
      type: file_path

required_capabilities:
  - python3.11

acceptance_criteria:
  - "pip install blueprint works (installs anthropic only)"
  - "pip install blueprint[openai] adds openai dependency"
  - "pip install blueprint[google] adds google-generativeai"
  - "pip install blueprint[all] installs all provider dependencies"
  - "pip install blueprint[outpost] adds boto3 for SSM"

verification:
  smoke:
    command: "python -c 'import blueprint'"
    timeout: PT10S
  unit:
    command: "pip install -e . && pip install -e .[all] --dry-run"
    timeout: PT1M

rollback: "git checkout HEAD -- pyproject.toml"

files_to_modify:
  - pyproject.toml

notes: |
  Use extras_require pattern for optional provider dependencies.
```

---

## Tier 3: Documentation & Polish

### T3.1: Update Documentation

```yaml
task_id: T3.1
name: "Document multi-provider usage"
status: not_started
dependencies: [T2.1, T2.2]

interface:
  input: "Refactored code, provider implementations"
  output: "Updated documentation with provider guide"

input_bindings: {}

output:
  location: file
  path: "docs/providers.md"
  ports:
    docs:
      type: file_path

required_capabilities:
  - python3.11

acceptance_criteria:
  - "Provider configuration documented"
  - "Examples for each provider"
  - "Migration guide (none needed if backwards compatible)"
  - "Environment variable reference"
  - "Troubleshooting section"

verification:
  smoke:
    command: "test -f docs/providers.md"
    timeout: PT5S

rollback: "git checkout HEAD -- docs/"

files_to_create:
  - docs/providers.md

files_to_modify:
  - docs/README.md

notes: |
  Keep documentation concise and example-driven.
```

---

### T3.2: Add Provider Selection CLI Flag

```yaml
task_id: T3.2
name: "Add --provider CLI flag to decomposer"
status: not_started
dependencies: [T2.1]

interface:
  input: "Refactored decomposer with provider support"
  output: "CLI with --provider option"

input_bindings:
  decomposer:
    source: T2.1
    output_port: decomposer
    transfer: file
    required: true

output:
  location: file
  path: "src/blueprint/cli.py"
  ports:
    cli:
      type: file_path

required_capabilities:
  - python3.11

acceptance_criteria:
  - "blueprint decompose --provider=openai 'goal' works"
  - "blueprint decompose --provider=anthropic 'goal' works (default)"
  - "blueprint providers list shows available providers"
  - "Invalid provider gives clear error message"

verification:
  smoke:
    command: "python -m blueprint.cli --help | grep provider"
    timeout: PT10S
  unit:
    command: "python -m pytest tests/test_cli.py -v"
    timeout: PT2M

rollback: "git checkout HEAD -- src/blueprint/cli.py"

files_to_modify:
  - src/blueprint/cli.py

files_to_create:
  - tests/test_cli.py

notes: |
  CLI should respect BLUEPRINT_PROVIDER env var as default.
  --provider flag overrides env var.
```

---

## Dependency Graph

```yaml
dependency_graph:
  T0.1:
    depends_on: []

  T0.2:
    depends_on: [T0.1]
    input_bindings:
      interface: T0.1.output.provider_interface

  T0.3:
    depends_on: [T0.1]
    input_bindings:
      interface: T0.1.output.provider_interface

  T1.1:
    depends_on: [T0.1, T0.3]
    parallel_group: "providers"

  T1.2:
    depends_on: [T0.1, T0.3]
    parallel_group: "providers"

  T1.3:
    depends_on: [T0.1, T0.3]
    parallel_group: "providers"

  T2.1:
    depends_on: [T0.2, T0.3]

  T2.2:
    depends_on: [T1.1, T1.2, T1.3]

  T3.1:
    depends_on: [T2.1, T2.2]
    parallel_group: "polish"

  T3.2:
    depends_on: [T2.1]
    parallel_group: "polish"
```

---

## Visual Dependency Graph

```
T0.1 (Provider Interface)
  │
  ├──► T0.2 (Anthropic Provider)──────┐
  │                                    │
  └──► T0.3 (Registry)────────────────┼──► T2.1 (Refactor Decomposer)──┬──► T3.1 (Docs)
         │                             │                                │
         ├──► T1.1 (OpenAI)  ──┐      │                                └──► T3.2 (CLI)
         │                      │      │
         ├──► T1.2 (Google)  ──┼──► T2.2 (Package Config)
         │                      │
         └──► T1.3 (Outpost) ──┘
```

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1.0 | 2026-01-05 | Claude Opus 4.5 | Initial Blueprint from fleet consultation |

---

*Blueprint Standard Format v2.0.2*
*"Universal AI Orchestration Contract"*
