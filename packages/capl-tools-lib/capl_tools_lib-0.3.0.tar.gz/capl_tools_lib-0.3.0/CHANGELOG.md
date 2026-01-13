# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.2.5] - 2026-01-04
### Docs
- Added documentation link to PyPI metadata.


## [0.2.4] - 2026-01-04


## [0.2.2] - 2026-01-04
### Fixed
- Aligned CLI command name with package name in `pyproject.toml` to improve `uvx` compatibility.

## [0.2.1] - 2026-01-04
### Removed
- CLI `validate` command (stub).

## [0.2.0] - 2026-01-04
### Added
- Comprehensive unit test suite for `CaplEditor`, `CaplProcessor`, and `CaplFileManager`.
- Automated documentation site using MkDocs and Material theme.
- Automated CLI reference generation using `mkdocs-typer2`.
- GitHub Actions workflow for automated documentation deployment.
- Development dependencies for testing (`pytest`, `pytest-cov`) and documentation.

### Changed
- Refactored `CaplEditor` to support initialization from raw line lists, improving testability.
- Updated `README.md` with testing and development instructions.

## [0.1.0] - 2026-01-04
### Added
- Initial release on PyPI.
- Core CAPL scanning functionality (Includes, Variables, Handlers, Functions, TestCases).
- High-level `CaplProcessor` facade.
- CLI tool with `scan` and `remove-group` commands.
- Basic project structure and documentation.

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
