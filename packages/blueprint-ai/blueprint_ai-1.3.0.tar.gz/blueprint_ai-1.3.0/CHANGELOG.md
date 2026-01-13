# Changelog

All notable changes to Blueprint will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-01-05

### Added
- **Multi-provider support**: Blueprint now supports multiple LLM providers
  - Anthropic (Claude) - default
  - OpenAI (GPT-4)
  - Google (Gemini)
  - Outpost (multi-agent dispatch)
- **Provider abstraction layer**: Clean registry pattern for provider management
- **CLI `--provider` flag**: Runtime provider selection via command line
- **Provider-specific optional dependencies**: Install only what you need
  - `pip install blueprint-ai[anthropic]`
  - `pip install blueprint-ai[openai]`
  - `pip install blueprint-ai[google]`
  - `pip install blueprint-ai[outpost]`
  - `pip install blueprint-ai[all-providers]`

### Changed
- GoalDecomposer refactored to use provider registry
- CLI updated to support provider selection
- Windows compatibility improvements (ASCII output instead of emoji)

### Fixed
- 215 tests now passing
- Aggregator, executor, and CLI test fixes
- Datetime handling improvements (timezone-aware)

## [1.2.0] - 2026-01-04

### Added
- Blueprint Spec v2.0.1 with medium priority fixes
- S3 output support for large Blueprints (no truncation)
- Outpost integration for zero-cost generation

### Changed
- Metadata block now mandatory for valid Blueprints
- BLUEPRINT_INTERFACE.md updated to v2.2

## [1.1.0] - 2026-01-03

### Added
- Initial PyPI release
- Blueprint generation from natural language goals
- Validation and execution pipeline
- CLI tool (`blueprint generate`, `blueprint validate`)

---

*Blueprint — "Goals become roadmaps"*
