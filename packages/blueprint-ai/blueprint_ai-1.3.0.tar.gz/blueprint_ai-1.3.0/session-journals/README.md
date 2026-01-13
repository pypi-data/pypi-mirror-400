# Session Journals

This directory contains session journals for Blueprint.

**IMPORTANT:** All session journals for this app are stored HERE, not in zeOS Core.

## Format

Journals follow the zeOS session journaling standard:
- Filename: `YYYY-MM-DD-NNN.md` (e.g., `2026-01-03-001.md`)
- Status: CHECKPOINT or COMPLETE
- Required fields: session_id, date, status, agent, next_action_primer

## Usage

- `!checkpoint` — Save progress mid-session (writes HERE)
- `!end` — Generate final journal and commit (writes HERE)

## Boot Command

```
!project blueprint
```

See zeOS Shell Protocol for full documentation.
