# Blueprint Session 2026-01-05 — Fleet Review of v2.0.0

## Session Focus: 5-Agent Critical Review of BLUEPRINT_SPEC v2.0.0

### Executive Summary

Dispatched all 5 Outpost agents (Claude, Codex, Gemini, Grok, DeepSeek) to critically review BLUEPRINT_SPEC v2.0.0 before implementation. Fleet consensus identified 5 blocking issues and ~10 high-priority fixes. Average score: **7.4/10**. Spec requires v2.0.1 patch before building.

---

## Fleet Scores

| Agent | Model | Rating | Key Finding |
|-------|-------|--------|-------------|
| **Claude** | claude-opus-4-5-20251101 | **7.5/10** | Schema compatibility undefined, transform language ambiguous |
| **Codex** | gpt-5.2-codex | **6/10** | Critical schema contradictions (dependencies vs dependency_graph) |
| **Gemini** | gemini-3-pro-preview | **7.5/10** | Unix assumptions, shared filesystem assumptions |
| **Grok** | grok-4-1-fast-reasoning | **9/10** | Production-grade, 4 fixes for 10/10 |
| **Aider** | deepseek-coder | **7/10** | 70% complete, missing 30% in critical paths |

**Fleet Average: 7.4/10**

---

## BLOCKING ISSUES (Must Fix Before Build)

### 1. Transform Language Undefined
**Lines**: 473, 480
**Problem**: `transform: ".items[0]"` — is it jq or JSONPath?
**Agents Flagged**: 5/5

**Fix**:
```yaml
transform:
  language: jq  # jq | jsonpath (mandate ONE)
  expression: ".items[0]"
```

---

### 2. Network Transfer Protocol Vague
**Lines**: 432-437
**Problem**: "HTTP/S3/message queue" is a list of options, not a contract
**Agents Flagged**: 5/5

**Fix**:
```yaml
output:
  location: network
  protocol: s3  # http | s3 | sqs | kafka
  endpoint: "s3://bucket/path"
  auth: "${secrets.AWS_ACCESS_KEY}"
  timeout: PT30S
```

---

### 3. Memory Transfer Cross-Executor Undefined
**Lines**: 432-437
**Problem**: What happens if agents switch mid-execution with `transfer: memory`?
**Agents Flagged**: 5/5

**Fix**: Add fallback rule:
```yaml
# If memory transfer crosses executor boundaries,
# automatically convert to file with JSON serialization
transfer:
  type: memory
  fallback: file
```

---

### 4. Schema Compatibility Undefined
**Lines**: 599-634
**Problem**: "Schemas are compatible (if provided)" — no definition of "compatible"
**Agents Flagged**: 4/5

**Fix**: Add explicit definition:
```markdown
## Schema Compatibility Definition

Output schema is **compatible** with input schema if:
1. All required input fields exist in output
2. Field types match or are coercible (int → float, null → any)
3. Nested objects follow same rules recursively

Example: Output `{a: int, b: string, c: array}` satisfies Input `{a: int, b: string}` ✅
```

---

### 5. Checkpoint State Fields Untyped
**Lines**: 527-530
**Problem**: `state_fields: [current_step, processed_items]` — how does executor know what these ARE?
**Agents Flagged**: 4/5

**Fix**:
```yaml
handoff:
  state_fields:
    - name: current_step
      path: "$.context.current_step"
      type: integer
    - name: processed_items
      path: "$.loop.processed_items"
      type: integer
  state_schema:
    type: object
    properties:
      current_step: { type: integer }
      processed_items: { type: integer }
```

---

## HIGH PRIORITY ISSUES (Should Fix)

### 6. Duplicate "Required Fields" Sections
**Lines**: 193-212 vs 214-251
**Problem**: Two separate Required Fields headers — unclear which fields are truly mandatory
**Fix**: Consolidate into single section with (v1.x) and (v2.0+) annotations

---

### 7. test_command vs verification Redundancy
**Lines**: 397-399
**Problem**: Both exist, unclear which wins if both present
**Fix**:
- Make `verification` block required
- Deprecate `test_command` (maps to verification.unit for backward compat)
- Add validation rule: if both exist, they must be identical

---

### 8. dependencies vs dependency_graph Conflict
**Lines**: 199, 638-689
**Problem**: Three places define dependencies — single source of truth unclear
**Fix**:
- `input_bindings` is authoritative for data dependencies
- `dependencies` list is for completion-only dependencies
- `dependency_graph` is computed/validated, not authored

---

### 9. Timeout Precedence Undefined
**Lines**: 287, 313, 365
**Problem**: timeout appears in resources, execution_context, and human_required
**Fix**: Define precedence: `resources.timeout` > `execution_context.timeout`

---

### 10. Output Required vs Backward Compat Contradiction
**Lines**: 965
**Problem**: v2.0 says output block required, but backward compat says missing defaults to stdout
**Fix**: Remove "defaults to stdout" — require `output` block in v2.0

---

### 11. Secret Resolution Enum Inconsistency
**Lines**: 175
**Problem**: `on_missing: abort|prompt|skip_task` but later `use_default` appears
**Fix**: Consolidate enum to: `abort | prompt | skip_task | use_default`

---

### 12. Checkpointed Status Transitions Undefined
**Lines**: 403
**Problem**: `checkpointed` status added but no state machine for transitions
**Fix**: Define transitions:
- `in_progress` → `checkpointed` (on interrupt)
- `checkpointed` → `in_progress` (on resume)
- `checkpointed` → `not_started` (on restart)

---

### 13. Parallel Group vs Locks Precedence
**Lines**: 660-665
**Problem**: If parallel_group and resource locks conflict, which wins?
**Fix**: Add rule: "Resource locks always take precedence over parallel_group membership"

---

### 14. Path Variable Substitution Rules
**Lines**: 259
**Problem**: No variable escaping rules, no documentation of all variables
**Fix**: Add appendix listing all variables: `${task_id}`, `${working_directory}`, `${blueprint_root}`

---

### 15. Output Cleanup/TTL Missing
**Lines**: N/A
**Problem**: No specification for when to clean up output files
**Fix**: Add `output.ttl: PT24H` or cleanup policy

---

## MEDIUM PRIORITY ISSUES

| Issue | Fix |
|-------|-----|
| Error message schema undefined | Add standardized error format |
| Logging format unspecified | Define log_format, log_level, log_destination |
| Capability version matching | `python3.11` means `>=3.11.0 <4.0.0` |
| Idempotency not declared | Add `idempotent: true | false` per task |
| Checkpoint conflict resolution | Define last-write-wins or optimistic locking |
| Missing executor reference impl | Create minimal compliant executor example |
| Unix-specific assumptions | Clarify POSIX requirement or add Windows support |
| Shared filesystem assumption | Document that `file` transfer requires same filesystem |

---

## Commits This Session

| Commit | Description |
|--------|-------------|
| `9c06034` | BLUEPRINT_INTERFACE v2.2 — S3 output (no truncation) |
| `7ea2593` | North Star established — Universal AI Orchestration Contract |
| `a41f090` | BLUEPRINT_SPEC v2.0.0 — Universal AI Orchestration Contract |

---

## Files Modified

- [README.md](../README.md) — North Star + Fleet Consensus table
- [BLUEPRINT_INTERFACE.md](../BLUEPRINT_INTERFACE.md) — S3 output for large Blueprints
- [docs/BLUEPRINT_SPEC_v2.md](../docs/BLUEPRINT_SPEC_v2.md) — v2.0.0 specification

---

## Next Session: v2.0.1 Patch

### Priority 1 (Blocking)
1. Define transform language (jq vs jsonpath)
2. Specify network transfer protocol fully
3. Add memory→file fallback rule
4. Define schema compatibility algorithm
5. Type checkpoint state fields

### Priority 2 (High)
6. Consolidate duplicate Required Fields sections
7. Resolve test_command vs verification
8. Define single source of truth for dependencies
9. Define timeout precedence
10. Remove backward compat contradiction

### Priority 3 (Medium)
11-20. Address remaining issues above

---

## Session Metadata

```yaml
session_id: "2026-01-05-fleet-review"
date: "2026-01-05"
status: COMPLETE
agent: "Claude Opus 4.5 (Persistence Executor)"
profile: "richie"
project: "Blueprint"
started: "2026-01-05T09:15:00Z"
completed: "2026-01-05T10:00:00Z"
```

---

*Blueprint: Universal AI Orchestration Contract — Fleet-Validated*
