# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


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
