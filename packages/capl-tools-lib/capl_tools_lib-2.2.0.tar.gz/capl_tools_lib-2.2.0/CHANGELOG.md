# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.1] - 2026-01-04

### Fix
- **release**: fix release notes extraction workflow

## [2.1.0] - 2026-01-04

### Refactor
- **cli**: remove --json option from scan command and fix tests

## [2.0.0] - 2026-01-04

### Feat
- unify remove command and implement TestGroup as an element

## [1.1.1] - 2026-01-04

### Fix
- restore dev_code.py original content

## [1.1.0] - 2026-01-04

### Feat
- integrate TOON for token-efficient LLM output

## [1.0.0] - 2026-01-04

### Feat
- implement semantic insert and AI-agent ready command system
- enhance CLI for AI-Agent readiness (JSON output, get/remove elements)

### Refactor
- improve GEMINI.md instructions
- update README with Agent-Ready CLI documentation

## [0.3.0] - 2026-01-04

### Feat
- add pre-commit hooks for commit message validation
- add a test feature for commitizen

## [0.2.5] - 2026-01-04

### Docs
- Added documentation link to PyPI metadata.

## [0.2.4] - 2026-01-04

## [0.2.3] - 2026-01-04

### Feat
- automate GitHub Release asset upload from dist folder

### Fix
- reorder build and release steps in release.yml and use manual check for release existence
- correct gh release create command arguments order in release.yml
- align cli command name with package name

## [0.2.2] - 2026-01-04

### Fix
- Aligned CLI command name with package name in `pyproject.toml` to improve `uvx` compatibility.
- update CHANGELOG.md for v0.2.3 to include release.yml fixes

## [0.2.1] - 2026-01-04

### Feat
- add GitHub Actions workflow for drafting releases

### Fix
- update release.yml to handle tag conflicts and bash errors

### Removed
- CLI `validate` command (stub).

## [0.2.0] - 2026-01-04

### Feat
- implement CLI with Typer and update docs
- **scanner**: implement stateful test group detection
- **scanner**: implement CaplScanner with decoupled strategies
- add CaplEditor class for CAPL file content editing
- **core**: Implement CaplFileManager for CAPL file operations
- **logging**: add centralized logging system in common.py
- **elements**: Add CaplInclude and CaplVariable classes

### Fix
- edit scan command summary feature to contains rich console

### Refactor
- rename core modules and implement processor pattern
- implement display_name and simplify CLI output
- Refactored `CaplEditor` to support initialization from raw line lists.

### Added
- Comprehensive unit test suite.
- Automated documentation site using MkDocs.
- Automated CLI reference generation.

## [0.1.0] - 2026-01-04

### Added
- Initial release on PyPI.
- Core CAPL scanning functionality.
- High-level `CaplProcessor` facade.
- CLI tool with `scan` and `remove-group` commands.
- Basic project structure and documentation.
## v2.2.0 (2026-01-05)

### Feat

- add property-based testing with hypothesis and improve parser robustness

## v2.1.1 (2026-01-04)

### Fix

- **release**: use native bash for changelog extraction
- **release**: use anton-palan/changelog-reader-action
- **release**: use re-actors/changelog-reader-action
- **release**: switch to softprops actions and simplify workflow
- **release**: use correct action and clean changelog
- **release**: fix release notes extraction workflow

## v2.1.0 (2026-01-04)

### Refactor

- **cli**: remove --json option from scan command and fix tests

## v2.0.0 (2026-01-04)

### Feat

- unify remove command and implement TestGroup as an element

## v1.1.1 (2026-01-04)

### Fix

- restore dev_code.py original content

## v1.1.0 (2026-01-04)

### Feat

- integrate TOON for token-efficient LLM output

## v1.0.0 (2026-01-04)

### Feat

- implement semantic insert and AI-agent ready command system
- enhance CLI for AI-Agent readiness (JSON output, get/remove elements)

### Refactor

- improve GEMINI.md instructions


- update README with Agent-Ready CLI documentation

## v0.3.0 (2026-01-04)

### Feat

- add pre-commit hooks for commit message validation
- add a test feature for commitizen

## v0.2.5 (2026-01-04)

## v0.2.4 (2026-01-04)

## v0.2.2 (2026-01-04)

### Fix

- update CHANGELOG.md for v0.2.3 to include release.yml fixes

## v0.2.3 (2026-01-04)

### Feat

- automate GitHub Release asset upload from dist folder

### Fix

- reorder build and release steps in release.yml and use manual check for release existence
- correct gh release create command arguments order in release.yml
- align cli command name with package name

## v0.2.1 (2026-01-04)

### Feat

- add GitHub Actions workflow for drafting releases

### Fix

- update release.yml to handle tag conflicts and bash errors

## v0.2.0 (2026-01-04)

### Feat

- implement CLI with Typer and update docs
- **scanner**: implement stateful test group detection
- **scanner**: implement CaplScanner with decoupled strategies
- add CaplEditor class for CAPL file content editing
- **core**: Implement CaplFileManager for CAPL file operations - Fix write_lines() method with automatic directory creation
- **core**: Implement CaplFileManager for CAPL file operations
- **logging**: add centralized logging system in common.py
- **elements**: Add CaplInclude and CaplVariable classes

### Fix

- edit scan command summary feature to contains rich console

### Refactor

- rename core modules and implement processor pattern
- implement display_name and simplify CLI output
