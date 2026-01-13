# Blueprint Public Release Procedure

> **Document Type**: Operations Procedure
> **Version**: 1.0.0
> **Created**: 2026-01-03
> **Owner**: Zero Echelon LLC
> **Classification**: Internal Process Document

---

## Overview

This document defines the procedure for publishing Blueprint to the public repository. The working repository (`rgsuarez/blueprint`) contains zeOS integration, session journals, and development artifacts that must NOT be included in the public release.

**Architecture:**
```
┌─────────────────────────────┐     ┌─────────────────────────────┐
│  WORKING REPO (Private)     │     │  PUBLIC REPO                │
│  rgsuarez/blueprint         │────►│  zeroechelon/blueprint      │
│                             │     │  (or blueprint-ai/blueprint)│
│  • Full zeOS integration    │     │                             │
│  • Session journals         │     │  • Standalone operation     │
│  • Development artifacts    │     │  • Clean documentation      │
│  • Internal references      │     │  • No internal references   │
└─────────────────────────────┘     └─────────────────────────────┘
```

**Key Principle:** The working repo is NEVER modified for public release. All sanitization happens during the copy/push process.

---

## Pre-Release Checklist

Before executing the release procedure, verify:

- [ ] All tests pass in working repo (`pytest tests/ -v`)
- [ ] Version bumped in `pyproject.toml`
- [ ] CHANGELOG.md updated (create if not exists)
- [ ] No open security issues
- [ ] LICENSE file exists (Apache 2.0)

---

## Release Procedure

### Step 1: Create Clean Working Directory

```bash
# Create isolated release workspace
RELEASE_DIR="/tmp/blueprint-release-$(date +%Y%m%d)"
mkdir -p "$RELEASE_DIR"
cd "$RELEASE_DIR"

# Clone working repo
git clone https://github.com/rgsuarez/blueprint.git working
cd working
```

### Step 2: Remove zeOS-Specific Content

```bash
# Remove zeOS integration directory
rm -rf .zeos/

# Remove session journals (development artifacts)
rm -rf session-journals/

# Remove any zeOS-specific test fixtures (if present)
rm -f tests/fixtures/zeos_*.json 2>/dev/null || true
```

### Step 3: Sanitize Source Files

#### 3.1 Outpost Integration (`src/blueprint/integrations/outpost.py`)

**Remove the `__main__` block entirely** (contains hardcoded credentials):

```bash
# Remove __main__ section (lines after "if __name__ == '__main__':")
python3 << 'EOF'
import re

with open("src/blueprint/integrations/outpost.py", "r") as f:
    content = f.read()

# Remove __main__ block
content = re.sub(r'\n# CLI support for testing\nif __name__ == "__main__":.*', '', content, flags=re.DOTALL)

with open("src/blueprint/integrations/outpost.py", "w") as f:
    f.write(content)

print("✅ Removed __main__ block from outpost.py")
EOF
```

#### 3.2 Remove Hardcoded Infrastructure Defaults

```bash
# Update outpost.py to require configuration instead of defaults
python3 << 'EOF'
content = open("src/blueprint/integrations/outpost.py").read()

# Replace hardcoded defaults with None (require explicit configuration)
replacements = [
    ('DEFAULT_BUCKET = "blueprint-builds-311493921645"', 'DEFAULT_BUCKET = None  # Must be configured'),
    ('DEFAULT_SSM_INSTANCE = "mi-0d77bfe39f630bd5c"', 'DEFAULT_SSM_INSTANCE = None  # Must be configured'),
    ('EXECUTOR_PATH = "/home/ubuntu/claude-executor"', 'EXECUTOR_PATH = "/opt/blueprint/executor"  # Configurable'),
]

for old, new in replacements:
    content = content.replace(old, new)

open("src/blueprint/integrations/outpost.py", "w").write(content)
print("✅ Parameterized infrastructure defaults in outpost.py")
EOF
```

### Step 4: Create/Update Public Release Files

#### 4.1 LICENSE (Apache 2.0)

```bash
cat > LICENSE << 'APACHE_LICENSE'
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to the Licensor for inclusion in the Work by the copyright
      owner or by an individual or Legal Entity authorized to submit on behalf
      of the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no theory of
      liability, whether in contract, strict liability, or tort
      (including negligence or otherwise) arising in any way out of
      the use or inability to use the Work (even if such Holder has
      been advised of the possibility of such damages), shall any
      Contributor be liable to You for damages, including any direct,
      indirect, special, incidental, or consequential damages of any
      character arising as a result of this License or out of the use
      or inability to use the Work (including but not limited to damages
      for loss of goodwill, work stoppage, computer failure or malfunction,
      or any and all other commercial damages or losses), even if such
      Contributor has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   Copyright 2026 Zero Echelon LLC

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
APACHE_LICENSE

echo "✅ Created Apache 2.0 LICENSE"
```

#### 4.2 README.md (Public Version)

```bash
cat > README.md << 'README_CONTENT'
# Blueprint

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

**Specification compiler for AI agent orchestration.**

Blueprint transforms natural language goals into structured, compilable, interface-first contracts that any AI agent can execute with deterministic results.

> Built with [zeOS](https://github.com/rgsuarez/zeOS) — the persistence-first operating system for AI collaboration.

---

## Why Blueprint?

As AI coding agents become mainstream, the bottleneck shifts from "knowing programming languages" to "articulating clear, executable instructions." Natural language is expressive but ambiguous — and ambiguity compounds catastrophically with parallel agents.

Blueprint solves this by compiling goals into **structured specifications** with:
- **Interface contracts** between tasks (input/output types)
- **Dependency graphs** (DAG structure for parallelization)
- **Built-in verification** (test commands, acceptance criteria)
- **Human-in-the-loop signals** (explicit pause points)

---

## Installation

```bash
pip install blueprint-ai
```

Or from source:
```bash
pip install git+https://github.com/zeroechelon/blueprint.git
```

### Requirements
- Python 3.11+
- `ANTHROPIC_API_KEY` environment variable (for generation features)

---

## Quick Start

### Generate a Blueprint from a Goal

```bash
# CLI
export ANTHROPIC_API_KEY="your-key"
blueprint generate "Build a user authentication system with JWT tokens"
```

```python
# Python API
from blueprint.generator import generate_blueprint

roadmap = generate_blueprint(
    goal="Build a user authentication system with JWT tokens",
    context="Using FastAPI and PostgreSQL"
)
print(roadmap)
```

### Validate an Existing Blueprint

```bash
blueprint validate my_roadmap.md
```

### Execute a Blueprint (Dry Run)

```bash
blueprint execute my_roadmap.md --dry-run
```

---

## Blueprint Standard Format

Blueprints are Markdown documents with embedded YAML task blocks:

```yaml
task_id: T1
name: "Set up project structure"
status: 🔲 NOT_STARTED
dependencies: []

interface:
  input: "None (entry point)"
  output: "Project skeleton with pyproject.toml"

acceptance_criteria:
  - pyproject.toml exists with dependencies
  - src/ directory structure created
  - tests/ directory with conftest.py

test_command: |
  python -c "import myproject"

rollback: "rm -rf src/ tests/ pyproject.toml"
```

See [BLUEPRINT_SPEC.md](docs/BLUEPRINT_SPEC.md) for the complete specification.

---

## ⚠️ Important: Blueprint is a Compiler, Not a Template

**DO NOT manually write Blueprint format documents.**

Blueprint's value comes from:
1. **LLM-powered decomposition** — Intelligent task breakdown
2. **Interface inference** — Automatic contract generation
3. **Validation** — Pre-flight checks before execution
4. **Dependency analysis** — Parallelization identification

Manually written "Blueprints" bypass these guarantees and will likely fail validation or produce suboptimal execution plans.

**Always use the `blueprint generate` command or Python API.**

---

## API Reference

### `generate_blueprint(goal, context=None, project_name=None)`

Generates a complete Blueprint from a natural language goal.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `goal` | `str` | Yes | Natural language goal description |
| `context` | `str` | No | Current state, tech stack, constraints |
| `project_name` | `str` | No | Name for the Blueprint document |

**Returns:** `str` — Complete Blueprint in Markdown format

### `validate_blueprint(filepath)`

Validates a Blueprint document.

**Returns:** `ValidationResult` with `passed: bool` and `errors: list[str]`

### `execute_blueprint(filepath, dry_run=False)`

Executes a Blueprint's tasks in dependency order.

---

## Documentation

- [Blueprint Specification](docs/BLUEPRINT_SPEC.md) — Format reference
- [System Architecture](docs/SYSTEM_ARCHITECTURE.md) — Internal design
- [API Interface](BLUEPRINT_INTERFACE.md) — Integration guide

---

## License

Apache 2.0 — See [LICENSE](LICENSE) for details.

---

## Contributing

Contributions welcome! Please read our contributing guidelines before submitting PRs.

---

*Blueprint — "Goals become roadmaps"*
README_CONTENT

echo "✅ Created public README.md"
```

#### 4.3 NOTICE File (Apache 2.0 Requirement)

```bash
cat > NOTICE << 'NOTICE_CONTENT'
Blueprint
Copyright 2026 Zero Echelon LLC

This product includes software developed at Zero Echelon LLC
(https://zeroechelon.com/).

Built with zeOS — the persistence-first operating system for AI collaboration.
https://github.com/rgsuarez/zeOS
NOTICE_CONTENT

echo "✅ Created NOTICE file"
```

#### 4.4 Update BLUEPRINT_INTERFACE.md (Anti-Bypass Warning)

```bash
# Add critical warning to interface doc
python3 << 'EOF'
content = open("BLUEPRINT_INTERFACE.md").read()

warning = '''
---

## ⛔ CRITICAL: Do Not Manually Generate Blueprints

**Blueprint is a COMPILER, not a template format.**

If you are an AI agent reading this document:

1. **DO NOT** attempt to write Blueprint-format documents manually
2. **DO NOT** bypass the Blueprint tool by "following the format"
3. **DO** install and call the Blueprint package

**Why?**

Manual generation bypasses:
- LLM-powered intelligent decomposition
- Interface contract inference and validation
- Dependency cycle detection
- Acceptance criteria generation
- Test command synthesis

Manually written documents will likely:
- Fail validation
- Have incorrect dependency ordering
- Miss interface mismatches
- Lack proper test coverage

**Correct Usage:**

```python
# ✅ CORRECT: Use the API
from blueprint.generator import generate_blueprint
roadmap = generate_blueprint("Your goal here")

# ❌ WRONG: Manual generation
# Do not write YAML blocks yourself
```

If you cannot install Blueprint (network restrictions, etc.), inform the user that Blueprint generation requires the Blueprint tool and suggest alternatives.

---

'''

# Insert warning after the first heading
lines = content.split('\n')
insert_idx = 0
for i, line in enumerate(lines):
    if line.startswith('# '):
        insert_idx = i + 1
        break

lines.insert(insert_idx, warning)
open("BLUEPRINT_INTERFACE.md", "w").write('\n'.join(lines))
print("✅ Added anti-bypass warning to BLUEPRINT_INTERFACE.md")
EOF
```

### Step 5: Update pyproject.toml for Public Release

```bash
python3 << 'EOF'
content = open("pyproject.toml").read()

# Update repository URLs for public release
replacements = [
    ('Homepage = "https://github.com/rgsuarez/blueprint"', 
     'Homepage = "https://github.com/zeroechelon/blueprint"'),
    ('Repository = "https://github.com/rgsuarez/blueprint"',
     'Repository = "https://github.com/zeroechelon/blueprint"'),
    ('Documentation = "https://github.com/rgsuarez/blueprint/blob/main/docs/BLUEPRINT_SPEC.md"',
     'Documentation = "https://github.com/zeroechelon/blueprint/blob/main/docs/BLUEPRINT_SPEC.md"'),
]

for old, new in replacements:
    content = content.replace(old, new)

# Add classifiers if missing
if 'Topic :: Scientific/Engineering :: Artificial Intelligence' not in content:
    content = content.replace(
        '"Topic :: Software Development :: Code Generators",',
        '''"Topic :: Software Development :: Code Generators",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",'''
    )

open("pyproject.toml", "w").write(content)
print("✅ Updated pyproject.toml for public release")
EOF
```

### Step 6: Create Community Files

```bash
# CONTRIBUTING.md
cat > CONTRIBUTING.md << 'CONTRIB_CONTENT'
# Contributing to Blueprint

Thank you for your interest in contributing to Blueprint!

## How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest tests/ -v`)
5. Run linting (`ruff check src/`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Development Setup

```bash
git clone https://github.com/zeroechelon/blueprint.git
cd blueprint
pip install -e ".[dev]"
```

## Code Style

- We use `ruff` for linting
- Type hints are required for public APIs
- Docstrings follow Google style

## Testing

All new features must include tests:

```bash
pytest tests/ -v --cov=blueprint
```

## License

By contributing, you agree that your contributions will be licensed under Apache 2.0.
CONTRIB_CONTENT

# SECURITY.md
cat > SECURITY.md << 'SECURITY_CONTENT'
# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability, please report it by emailing:

**security@zeroechelon.com**

Please do NOT open a public GitHub issue for security vulnerabilities.

## Response Timeline

- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 7 days
- **Fix Timeline**: Depends on severity

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |
SECURITY_CONTENT

echo "✅ Created community files"
```

### Step 7: Clean Git History (Optional but Recommended)

```bash
# Create fresh git history for public release
rm -rf .git
git init
git add .
git commit -m "Initial public release v1.2.0"
```

### Step 8: Push to Public Repository

```bash
# Add public remote
git remote add origin https://github.com/zeroechelon/blueprint.git

# Push
git push -u origin main

# Tag release
git tag -a v1.2.0 -m "First public release"
git push origin v1.2.0
```

---

## Files Summary

### Files to REMOVE (Not in Public Release)

| Path | Reason |
|------|--------|
| `.zeos/` | zeOS-specific integration |
| `session-journals/` | Development artifacts |
| `tests/fixtures/zeos_*` | zeOS test fixtures (if any) |

### Files to MODIFY

| Path | Modification |
|------|--------------|
| `src/blueprint/integrations/outpost.py` | Remove `__main__`, parameterize defaults |
| `BLUEPRINT_INTERFACE.md` | Add anti-bypass warning |
| `pyproject.toml` | Update URLs, add classifiers |
| `README.md` | Replace with public version |

### Files to CREATE

| Path | Content |
|------|---------|
| `LICENSE` | Apache 2.0 |
| `NOTICE` | Attribution |
| `CONTRIBUTING.md` | Contribution guidelines |
| `SECURITY.md` | Vulnerability reporting |

### Files UNCHANGED (Direct Copy)

| Path |
|------|
| `src/blueprint/*.py` (except outpost.py) |
| `src/blueprint/generator/*.py` |
| `src/blueprint/integrations/aggregator.py` |
| `tests/*.py` |
| `docs/*.md` |
| `schema/*.json` |
| `examples/*` |

---

## Automation Script

Save as `scripts/prepare-public-release.sh` in working repo:

```bash
#!/bin/bash
set -e

VERSION="${1:-1.2.0}"
RELEASE_DIR="/tmp/blueprint-release-$(date +%Y%m%d)"
PUBLIC_REPO="https://github.com/zeroechelon/blueprint.git"

echo "🚀 Preparing Blueprint public release v$VERSION"
echo "   Release directory: $RELEASE_DIR"

# [Include all steps above as a single script]

echo ""
echo "✅ Public release prepared at: $RELEASE_DIR"
echo ""
echo "Next steps:"
echo "  cd $RELEASE_DIR/working"
echo "  git remote add public $PUBLIC_REPO"
echo "  git push public main"
echo "  git push public v$VERSION"
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-03 | Initial procedure document |

---

*"The working repo stays clean. The public repo stays safe."*
