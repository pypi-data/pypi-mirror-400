#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# Blueprint Public Release Script v2.0
# ═══════════════════════════════════════════════════════════════
# Incorporates fleet feedback from Outpost multi-agent review
# 
# Usage:
#   ./prepare-public-release.sh [--dry-run] [--skip-pypi]
#
# Prerequisites:
#   - GitHub CLI (gh) authenticated to zeroechelon org
#   - PyPI API token in ~/.pypirc or TWINE_PASSWORD env var
#   - Python 3.11+ with pip, build, twine
# ═══════════════════════════════════════════════════════════════

set -euo pipefail

# ─────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────
WORKING_REPO="https://github.com/rgsuarez/blueprint.git"
PUBLIC_REPO="zeroechelon/blueprint"
PUBLIC_REPO_URL="https://github.com/zeroechelon/blueprint.git"
RELEASE_DIR="/tmp/blueprint-release-$(date +%Y%m%d-%H%M%S)"
PYPI_PACKAGE_NAME="blueprint-ai"

# Parse arguments
DRY_RUN=false
SKIP_PYPI=false
for arg in "$@"; do
    case $arg in
        --dry-run) DRY_RUN=true ;;
        --skip-pypi) SKIP_PYPI=true ;;
        *) echo "Unknown argument: $arg"; exit 1 ;;
    esac
done

# ─────────────────────────────────────────────────────────────────
# Cleanup trap (fleet recommendation: always clean up on failure)
# ─────────────────────────────────────────────────────────────────
cleanup() {
    if [ -d "$RELEASE_DIR" ] && [ "$DRY_RUN" = false ]; then
        echo "🧹 Cleaning up $RELEASE_DIR"
        rm -rf "$RELEASE_DIR"
    fi
}
trap cleanup EXIT

# ─────────────────────────────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────────────────────────────
log() { echo "$(date +%H:%M:%S) │ $1"; }
success() { echo "$(date +%H:%M:%S) │ ✅ $1"; }
warn() { echo "$(date +%H:%M:%S) │ ⚠️  $1"; }
error() { echo "$(date +%H:%M:%S) │ ❌ $1"; exit 1; }

confirm() {
    if [ "$DRY_RUN" = true ]; then
        echo "[DRY-RUN] Would prompt: $1"
        return 0
    fi
    read -p "$1 (y/N) " -n 1 -r
    echo
    [[ $REPLY =~ ^[Yy]$ ]]
}

# ─────────────────────────────────────────────────────────────────
# PHASE 1: Pre-flight checks
# ─────────────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "🚀 BLUEPRINT PUBLIC RELEASE v2.0"
echo "═══════════════════════════════════════════════════════════════"
echo "Working Repo:  $WORKING_REPO"
echo "Public Repo:   $PUBLIC_REPO"
echo "Release Dir:   $RELEASE_DIR"
echo "Dry Run:       $DRY_RUN"
echo "Skip PyPI:     $SKIP_PYPI"
echo "═══════════════════════════════════════════════════════════════"
echo ""

log "Phase 1: Pre-flight checks..."

# Check required tools
for tool in git python3 pip; do
    command -v $tool >/dev/null 2>&1 || error "Required tool not found: $tool"
done
success "Required tools available"

# ─────────────────────────────────────────────────────────────────
# PHASE 2: Clone and sanitize
# ─────────────────────────────────────────────────────────────────
log "Phase 2: Creating sanitized copy..."

mkdir -p "$RELEASE_DIR"
cd "$RELEASE_DIR"

log "Cloning working repository..."
if [ "$DRY_RUN" = true ]; then
    echo "[DRY-RUN] Would clone $WORKING_REPO"
    mkdir -p working
else
    git clone "$WORKING_REPO" working
fi
cd working

# ─────────────────────────────────────────────────────────────────
# PHASE 2a: Remove sensitive directories (block-list)
# ─────────────────────────────────────────────────────────────────
log "Removing zeOS-specific content..."

REMOVE_PATHS=(
    ".zeos"
    "session-journals"
    ".env"
    ".env.*"
    "secrets"
    "config/local"
)

for path in "${REMOVE_PATHS[@]}"; do
    if [ "$DRY_RUN" = true ]; then
        echo "[DRY-RUN] Would remove: $path"
    else
        rm -rf "$path" 2>/dev/null || true
    fi
done

# Remove backup files
if [ "$DRY_RUN" = false ]; then
    find . -name "*.bak" -delete 2>/dev/null || true
    find . -name "*.backup" -delete 2>/dev/null || true
    find . -name "*.orig" -delete 2>/dev/null || true
fi
success "Removed sensitive directories"

# ─────────────────────────────────────────────────────────────────
# PHASE 2b: Sanitize source code
# ─────────────────────────────────────────────────────────────────
log "Sanitizing source files..."

if [ "$DRY_RUN" = false ]; then
    # Remove __main__ block from outpost.py (contains test credentials)
    python3 << 'PYTHON_SANITIZE'
import re
import sys

outpost_path = "src/blueprint/integrations/outpost.py"

try:
    with open(outpost_path, "r") as f:
        content = f.read()
    
    # Remove __main__ block (contains hardcoded test values)
    content = re.sub(
        r'\n# CLI support for testing\nif __name__ == "__main__":.*',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Parameterize infrastructure defaults
    replacements = [
        ('DEFAULT_BUCKET = "blueprint-builds-311493921645"', 
         'DEFAULT_BUCKET = None  # Configure via BLUEPRINT_S3_BUCKET env var'),
        ('DEFAULT_SSM_INSTANCE = "mi-0d77bfe39f630bd5c"',
         'DEFAULT_SSM_INSTANCE = None  # Configure via BLUEPRINT_SSM_INSTANCE env var'),
        ('EXECUTOR_PATH = "/home/ubuntu/claude-executor"',
         'EXECUTOR_PATH = "/opt/blueprint/executor"  # Override via BLUEPRINT_EXECUTOR_PATH'),
    ]
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    with open(outpost_path, "w") as f:
        f.write(content)
    
    print("✅ Sanitized outpost.py")
except FileNotFoundError:
    print("⚠️  outpost.py not found, skipping")
except Exception as e:
    print(f"❌ Error sanitizing outpost.py: {e}")
    sys.exit(1)
PYTHON_SANITIZE
fi

# ─────────────────────────────────────────────────────────────────
# PHASE 2c: Security scan (fleet recommendation)
# ─────────────────────────────────────────────────────────────────
log "Running security verification scan..."

SENSITIVE_PATTERNS=(
    'AKIA[0-9A-Z]{16}'                    # AWS Access Key IDs
    'sk-[a-zA-Z0-9]{48}'                  # OpenAI API keys
    'sk-ant-[a-zA-Z0-9-]{90,}'            # Anthropic API keys
    'ghp_[a-zA-Z0-9]{36}'                 # GitHub PATs (new format)
    'github_pat_[a-zA-Z0-9_]{80,}'        # GitHub PATs (fine-grained)
    'mi-[0-9a-f]{17}'                     # AWS SSM Instance IDs
    '[0-9]{12}'                           # AWS Account IDs (12 digits)
    'password\s*=\s*["\047][^"\047]+'     # Hardcoded passwords
    'secret\s*=\s*["\047][^"\047]+'       # Hardcoded secrets
)

FOUND_SENSITIVE=false

if [ "$DRY_RUN" = false ]; then
    for pattern in "${SENSITIVE_PATTERNS[@]}"; do
        # Search but exclude .git, node_modules, and this script itself
        matches=$(grep -r -E --include="*.py" --include="*.md" --include="*.json" \
            "$pattern" . 2>/dev/null | \
            grep -v ".git" | \
            grep -v "SENSITIVE_PATTERNS" | \
            grep -v "# AWS Access Key" || true)
        
        if [ -n "$matches" ]; then
            echo "⚠️  Potential sensitive pattern found: $pattern"
            echo "$matches" | head -5
            FOUND_SENSITIVE=true
        fi
    done
    
    if [ "$FOUND_SENSITIVE" = true ]; then
        warn "Security scan found potential sensitive data"
        if ! confirm "Continue anyway? Review the matches above carefully."; then
            error "Aborted due to security concerns"
        fi
    else
        success "Security scan passed - no sensitive patterns found"
    fi
fi

# ─────────────────────────────────────────────────────────────────
# PHASE 3: Create release files
# ─────────────────────────────────────────────────────────────────
log "Phase 3: Creating release files..."

if [ "$DRY_RUN" = false ]; then

# 3.1 Apache 2.0 LICENSE
cat > LICENSE << 'LICENSE_TEXT'
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
      control with that entity.

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
      Object form, made available under the License.

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work, that is intentionally submitted to the Licensor.

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor.

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
      use, offer to sell, sell, import, and otherwise transfer the Work.

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
          attribution notices from the Source form of the Work.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND.

   8. Limitation of Liability. In no event and under no theory of
      liability shall any Contributor be liable to You for damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work, You may choose to offer acceptance of support, warranty,
      indemnity, or other liability obligations consistent with this License.

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
LICENSE_TEXT

# 3.2 NOTICE file
cat > NOTICE << 'NOTICE_TEXT'
Blueprint
Copyright 2026 Zero Echelon LLC

This product includes software developed at Zero Echelon LLC
(https://zeroechelon.com/).

Built with zeOS — the persistence-first operating system for AI collaboration.
https://github.com/rgsuarez/zeOS
NOTICE_TEXT

# 3.3 Public README
cat > README.md << 'README_TEXT'
# Blueprint

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PyPI](https://img.shields.io/pypi/v/blueprint-ai.svg)](https://pypi.org/project/blueprint-ai/)

**Specification compiler for AI agent orchestration.**

Blueprint transforms natural language goals into structured, compilable, interface-first contracts that any AI agent can execute with deterministic results.

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

Or with LLM support for generation features:
```bash
pip install blueprint-ai[llm]
```

### Requirements
- Python 3.11+
- `ANTHROPIC_API_KEY` environment variable (for generation features)

---

## Quick Start

### Generate a Blueprint from a Goal

```bash
export ANTHROPIC_API_KEY="your-key"
blueprint generate "Build a user authentication system with JWT tokens"
```

```python
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

**Always use the `blueprint generate` command or Python API.**

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

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting PRs.

---

*Blueprint — "Goals become roadmaps"*
README_TEXT

# 3.4 CONTRIBUTING.md
cat > CONTRIBUTING.md << 'CONTRIB_TEXT'
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
CONTRIB_TEXT

# 3.5 SECURITY.md
cat > SECURITY.md << 'SECURITY_TEXT'
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
SECURITY_TEXT

success "Created release files"

fi  # end DRY_RUN check

# ─────────────────────────────────────────────────────────────────
# PHASE 3b: Update pyproject.toml
# ─────────────────────────────────────────────────────────────────
log "Updating pyproject.toml for public release..."

if [ "$DRY_RUN" = false ]; then
    python3 << 'PYTHON_UPDATE_TOML'
import re

with open("pyproject.toml", "r") as f:
    content = f.read()

# Update package name for PyPI
content = re.sub(r'name = "blueprint"', 'name = "blueprint-ai"', content)

# Update license
content = re.sub(r'license = "MIT"', 'license = "Apache-2.0"', content)

# Update license classifier
content = re.sub(
    r'"License :: OSI Approved :: MIT License"',
    '"License :: OSI Approved :: Apache Software License"',
    content
)

# Update URLs to public repo
content = re.sub(
    r'https://github\.com/rgsuarez/blueprint',
    'https://github.com/zeroechelon/blueprint',
    content
)

# Add AI classifier if not present
if "Scientific/Engineering :: Artificial Intelligence" not in content:
    content = re.sub(
        r'("Topic :: Software Development :: Code Generators",)',
        r'\1\n    "Topic :: Scientific/Engineering :: Artificial Intelligence",',
        content
    )

with open("pyproject.toml", "w") as f:
    f.write(content)

print("✅ Updated pyproject.toml")
PYTHON_UPDATE_TOML
fi

# ─────────────────────────────────────────────────────────────────
# PHASE 4: Validation
# ─────────────────────────────────────────────────────────────────
log "Phase 4: Validation..."

if [ "$DRY_RUN" = false ]; then
    # Install dependencies
    log "Installing dependencies..."
    pip install -q build twine pytest
    
    # Build package
    log "Building distribution packages..."
    python -m build
    
    # Verify package
    log "Verifying built packages..."
    twine check dist/*
    
    # Test installation
    log "Testing installation in clean environment..."
    python -m venv /tmp/blueprint-test-env
    source /tmp/blueprint-test-env/bin/activate
    pip install -q dist/*.whl
    python -c "from blueprint.parser import parse_blueprint; print('✅ Import successful')"
    blueprint --help > /dev/null && echo "✅ CLI works"
    deactivate
    rm -rf /tmp/blueprint-test-env
    
    success "Package validation passed"
fi

# ─────────────────────────────────────────────────────────────────
# PHASE 5: Git setup and publish
# ─────────────────────────────────────────────────────────────────
log "Phase 5: Prepare for publication..."

VERSION=$(grep '^version = ' pyproject.toml 2>/dev/null | cut -d'"' -f2 || echo "1.2.0")
echo "Release version: $VERSION"

if [ "$DRY_RUN" = false ]; then
    # Fresh git history
    rm -rf .git
    git init
    git add .
    git commit -m "Initial public release v$VERSION"
    git tag -a "v$VERSION" -m "Release v$VERSION"
    
    success "Git repository initialized with tag v$VERSION"
    
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "📋 MANUAL STEPS REQUIRED"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    echo "1. Create public repository:"
    echo "   gh repo create $PUBLIC_REPO --public --source=. --push"
    echo ""
    echo "   OR manually:"
    echo "   git remote add origin $PUBLIC_REPO_URL"
    echo "   git push -u origin main"
    echo "   git push origin v$VERSION"
    echo ""
    
    if [ "$SKIP_PYPI" = false ]; then
        echo "2. Publish to PyPI:"
        echo "   twine upload dist/*"
        echo ""
        echo "3. Verify installation:"
        echo "   pip install $PYPI_PACKAGE_NAME"
        echo ""
    fi
    
    echo "Release directory: $RELEASE_DIR/working"
    echo "═══════════════════════════════════════════════════════════════"
else
    echo ""
    echo "[DRY-RUN] Would create git repo and prepare for push"
    echo "[DRY-RUN] Release would be at: $RELEASE_DIR/working"
fi

echo ""
success "Public release preparation complete!"
