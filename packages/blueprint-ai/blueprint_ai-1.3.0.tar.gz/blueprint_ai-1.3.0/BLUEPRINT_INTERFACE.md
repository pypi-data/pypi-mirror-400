# Blueprint Interface Specification v2.2

> **Cross-Project API Contract for AI-Powered Roadmap Generation**
> **v2.2 Change:** S3 output for large Blueprints (no more truncation)

This document enables any AI agent to invoke Blueprint's generation pipeline to transform goals into structured, executable roadmaps.

---

## Quick Start: Outpost Generation (RECOMMENDED)

This method uses your existing Outpost subscription. **No API fees.**

### Prerequisites

- Outpost server accessible (SSM instance: `mi-0bbd8fed3f0650ddb`)
- AWS credentials configured
- Blueprint repo cloned on Outpost server

### Generation Command

```bash
aws ssm send-command \
  --instance-ids "mi-0bbd8fed3f0650ddb" \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["sudo -u ubuntu /home/ubuntu/claude-executor/dispatch-unified.sh blueprint \"Generate a Blueprint specification for: BUILD_A_USER_AUTH_SYSTEM_WITH_JWT. Read docs/BLUEPRINT_SPEC.md for the exact format. IMPORTANT: Include the BLUEPRINT METADATA comment block immediately after the header. Output only the complete markdown document.\" --executor=claude --context"]' \
  --output-s3-bucket-name "outpost-outputs" \
  --output-s3-key-prefix "blueprints/" \
  --query 'Command.CommandId' \
  --output text
```

**Replace** `BUILD_A_USER_AUTH_SYSTEM_WITH_JWT` with your actual goal.

**Key flags:**
- `blueprint` = repo name (context loads from here)
- `--executor=claude` = Claude Code (Opus 4.5)
- `--context` = injects Blueprint project knowledge
- `--output-s3-bucket-name` = routes output to S3 (bypasses 24KB SSM limit)

### Get Results

Wait 60-120 seconds, check status:

```bash
aws ssm get-command-invocation \
  --command-id "COMMAND_ID_HERE" \
  --instance-id "mi-0bbd8fed3f0650ddb" \
  --query 'Status' \
  --output text
```

Once status is `Success`, retrieve from S3:

```bash
aws s3 cp s3://outpost-outputs/blueprints/COMMAND_ID_HERE/mi-0bbd8fed3f0650ddb/awsrunShellScript/0.awsrunShellScript/stdout ./blueprint_output.txt --profile soc
```

### Save the Blueprint

Extract the markdown (starts with `# `) and save to your project:

```bash
# The output contains the full Blueprint
# Save to your target project's docs/ directory
```

> **Note:** Blueprints can exceed 24KB. Always use S3 output to avoid truncation.

---

## For AI Agents: Step-by-Step

If you are an AI agent (Claude Code, etc.) and need to generate a Blueprint:

### 1. Prepare Your Goal

Format your goal clearly:

```
GOAL: [What you want to build]

CONTEXT:
- Tech stack: [languages, frameworks]
- Current state: [what exists]
- Constraints: [must use X, cannot change Y]
```

### 2. Dispatch to Outpost

Use SSM to send the generation task with S3 output:

```bash
aws ssm send-command \
  --instance-ids "mi-0bbd8fed3f0650ddb" \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["sudo -u ubuntu /home/ubuntu/claude-executor/dispatch-unified.sh blueprint \"Generate a Blueprint specification for: YOUR_GOAL_HERE. Context: YOUR_CONTEXT_HERE. Read docs/BLUEPRINT_SPEC.md for format. CRITICAL: Include the BLUEPRINT METADATA comment block after the header. Output only the Blueprint markdown.\" --executor=claude --context"]' \
  --output-s3-bucket-name "outpost-outputs" \
  --output-s3-key-prefix "blueprints/" \
  --query 'Command.CommandId' \
  --output text
```

### 3. Poll for Completion

```bash
aws ssm get-command-invocation \
  --command-id "CMD_ID" \
  --instance-id "mi-0bbd8fed3f0650ddb" \
  --query 'Status' \
  --output text
```

Wait until status is `Success`.

### 4. Retrieve from S3 and Save

```bash
aws s3 cp s3://outpost-outputs/blueprints/CMD_ID/mi-0bbd8fed3f0650ddb/awsrunShellScript/0.awsrunShellScript/stdout ./blueprint_output.txt --profile soc
```

Parse the markdown from the output and save to your project.

> **Important:** Do NOT use `StandardOutputContent` — it truncates at 24KB. Always retrieve from S3.

---

## CRITICAL: Blueprint is a Compiler, Not a Template

**DO NOT manually write Blueprint-format documents.**

### Why This Matters

Blueprint's value is the **compilation pipeline**, not the format:

| Stage | What It Does | Manual = Broken |
|-------|--------------|-----------------|
| Decomposition | Optimal atomic task breakdown | You guess |
| Interface Inference | Input/output contracts | You guess |
| Dependency Analysis | Cycle detection, parallelization | You miss cycles |
| Test Generation | Concrete verification commands | Generic/missing |

### Detection of Valid Blueprints

Legitimate Blueprints contain metadata:

```
<!-- BLUEPRINT METADATA (DO NOT REMOVE) -->
<!-- _blueprint_version: 1.4.0 -->
<!-- _generated_at: 2026-01-04T12:00:00Z -->
<!-- _generator: blueprint.generator -->
<!-- END METADATA -->
```

Documents without these markers may fail validation.

---

## Alternative: Python API

If you have `ANTHROPIC_API_KEY` and prefer direct API (incurs fees):

```bash
pip install blueprint-ai
```

```python
from blueprint.generator import generate_blueprint

markdown = generate_blueprint(
    goal="Build a user authentication system with JWT",
    context="Tech Stack: Python, FastAPI, PostgreSQL"
)

with open("docs/MASTER_ROADMAP.md", "w") as f:
    f.write(markdown)
```

---

## Best Practices

### Effective Goals

**Good:**
```
Build a user authentication system with email/password login,
OAuth2 social login (Google, GitHub), password reset via email,
and session management with JWT tokens
```

**Bad:**
```
Add login
```

### Provide Context

Include: current state, tech stack, constraints, team size.

### Task Count Guidelines

| Complexity | Tasks | Example |
|------------|-------|---------|
| Small | 5-15 | Password reset |
| Medium | 15-30 | User management |
| Large | 30-50 | Complete auth overhaul |
| Too large | >50 | Break into sub-Blueprints |

---

## After Generation: Execution

Once you have a Blueprint, execute via:

1. **Manual**: Implement tasks yourself
2. **Outpost**: Dispatch each task to agents
3. **Claude Code**: Feed Blueprint for implementation

Example task execution:

```bash
aws ssm send-command \
  --instance-ids "mi-0bbd8fed3f0650ddb" \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["sudo -u ubuntu /home/ubuntu/claude-executor/dispatch-unified.sh YOUR_REPO \"Implement T1: Set up project structure per Blueprint\" --executor=claude --context"]' \
  --query 'Command.CommandId' \
  --output text
```

---

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| `NO_RESPONSE_YET` | Still processing | Wait 60-120 seconds |
| `status: timeout` | Goal too complex | Simplify or increase timeout |
| Malformed output | LLM didn't follow format | Retry with clearer goal |
| Truncated output | Used `StandardOutputContent` | Use S3 retrieval instead |

---

## Related Documents

- [BLUEPRINT_SPEC.md](docs/BLUEPRINT_SPEC.md) — Format specification
- [OUTPOST_INTERFACE.md](https://github.com/rgsuarez/outpost/blob/main/OUTPOST_INTERFACE.md) — Outpost dispatch contract

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-03 | Initial release |
| 1.1 | 2026-01-03 | Anti-bypass warning |
| 2.0 | 2026-01-04 | Outpost-based generation |
| 2.1 | 2026-01-05 | Metadata block mandatory |
| 2.2 | 2026-01-05 | **S3 output (no more truncation)** |

---

*Blueprint v2.2 — "Goals become roadmaps"*
