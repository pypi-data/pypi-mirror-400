# Blueprint

> **Universal AI Orchestration Contract**

Blueprint is the industry-standard specification format for multi-agent AI execution. Any flagship model — Claude, GPT, Gemini, Grok, DeepSeek — can parse, execute, and hand off Blueprint tasks with zero ambiguity.

**North Star:** A specification so precise that any AI agent can execute it identically, hand off to any other agent mid-task, and verify completion deterministically.

## What Blueprint Does

```
[Your Goal] → blueprint generate → [Perfect Specification]
```

You describe what you want. Blueprint produces a detailed, machine-parseable specification so precise that any AI agent — Claude, GPT, Gemini, Grok, DeepSeek, or future models — can execute it without ambiguity.

**Fleet-Validated:** This spec has been reviewed and approved by 5 frontier AI models (Claude Opus 4.5, GPT-5.2 Codex, Gemini 3 Pro, Grok 4, DeepSeek Coder) for parseability, executability, and hand-off reliability.

## What Blueprint Does NOT Do

Blueprint does not execute tasks. Blueprint does not orchestrate agents. Blueprint does not manage workflows.

**Blueprint generates the blueprint. That's it.**

What you do with the blueprint afterward is your business. Feed it to Claude Code. Parse it with your own tooling. Hand it to a human developer. We don't care. Our job ends when the specification is generated.

## Why This Matters

As AI coding agents become mainstream, the bottleneck shifts from "knowing how to code" to "knowing how to specify."

Natural language is ambiguous:
- "Build a login system" → What auth method? What database? What error handling?

Ambiguity at scale is catastrophic. Fifty agents misinterpreting fifty tasks = chaos.

**Blueprint eliminates ambiguity.** Every task in a Blueprint has:
- Typed interfaces (JSON Schema for inputs/outputs)
- Execution context (working directory, environment, required tools)
- Testable acceptance criteria (shell commands, not prose)
- Defined error policy (retry logic, failure actions)
- Clear dependencies (DAG structure)
- Rollback procedures (undo commands)

AI agents don't interpret a Blueprint. They execute it.

## Installation

```bash
pip install blueprint-ai
```

## Usage

```bash
# Set your LLM provider (auto-detects from environment)
export ANTHROPIC_API_KEY="sk-ant-..."
# or
export OPENAI_API_KEY="sk-..."

# Generate a blueprint
blueprint generate "Build a REST API for user management with JWT auth" -o api.bp.md

# That's it. Blueprint's job is done.
# Now feed api.bp.md to your preferred AI agent:
claude-code "Execute T1 from api.bp.md"
aider --message "Implement task T1.1 from api.bp.md"
```

## Example Output

Blueprint generates structured specifications like this:

```yaml
task_id: T1.2
name: "Implement JWT token validation"
status: not_started
dependencies: [T1.1]

interface:
  input: "JWT token and secret key"
  input_type: json
  input_schema:
    type: object
    properties:
      token: { type: string }
      secret: { type: string, minLength: 32 }
    required: [token, secret]
  output: "Validated claims or error"
  output_type: json
  output_schema:
    type: object
    properties:
      valid: { type: boolean }
      claims: { type: object }

execution_context:
  working_directory: "/project"
  environment_variables:
    PYTHONPATH: "/project/src"
  required_tools: [python3, pytest]
  timeout_seconds: 300

acceptance_criteria:
  - "Validates JWT signature using HS256"
  - "Rejects expired tokens"
  - "Returns claims on valid token"

test_command: "pytest tests/test_jwt.py -v"

on_failure:
  max_retries: 2
  action: block

rollback: "git checkout HEAD~1 -- src/auth/jwt.py"
```

No ambiguity. No guesswork. Just executable specifications.

## Philosophy

Think of Blueprint like an architect's drawings. An architect doesn't build the house — they produce specifications so precise that any competent builder can construct exactly what was envisioned.

We are the architect. The blueprint is our deliverable. Everything else is construction.

## Fleet Consensus (5/5 Models Agree)

Five frontier AI models independently reviewed Blueprint and reached consensus on what makes it the universal standard:

| Model | Verdict | Key Insight |
|-------|---------|-------------|
| **Claude Opus 4.5** | Approved | "P0: Define output persistence and hand-off protocol" |
| **GPT-5.2 Codex** | Approved | "Canonical machine schema needed for whole document" |
| **Gemini 3 Pro** | Approved | "Orchestrator-mediated hand-off with capability matching" |
| **Grok 4** | Approved | "File-based handshake protocol scales to 100+ agents" |
| **DeepSeek Coder** | Approved | "Add input_bindings syntax for explicit data flow" |

Full fleet review available in [session-journals/](session-journals/).

## Documentation

- [BLUEPRINT_INTERFACE.md](BLUEPRINT_INTERFACE.md) — How to generate Blueprints
- [BLUEPRINT_SPEC.md](docs/BLUEPRINT_SPEC.md) — The specification format (v1.4.0)

## License

Apache 2.0

---

*Blueprint: Universal AI Orchestration Contract*
