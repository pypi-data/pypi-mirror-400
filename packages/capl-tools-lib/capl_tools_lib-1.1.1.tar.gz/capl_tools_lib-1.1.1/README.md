# CAPL_Parser

[![PyPI version](https://img.shields.io/pypi/v/capl-tools-lib.svg)](https://pypi.org/project/capl-tools-lib/)
[![Python versions](https://img.shields.io/pypi/pyversions/capl-tools-lib.svg)](https://pypi.org/project/capl-tools-lib/)
[![Release](https://github.com/MohamedHamed19m/CAPL_Parser/actions/workflows/release.yml/badge.svg)](https://github.com/MohamedHamed19m/CAPL_Parser/actions/workflows/release.yml)
[![publish-docs](https://github.com/MohamedHamed19m/CAPL_Parser/actions/workflows/docs.yml/badge.svg)](https://github.com/MohamedHamed19m/CAPL_Parser/actions/workflows/docs.yml)

A powerful command-line tool for parsing, analyzing, and manipulating CAPL (CAN Access Programming Language) files.

## Features

- **Parse CAPL Files** – Extract and analyze CAPL code structure
- **Test Group Detection** – Identify and organize test cases into logical groups (e.g., via `InitializeTestGroup`)
- **Manipulate & Transform** – Modify CAPL code programmatically
- **AST Operations** – Work with abstract syntax trees
- **Validation** – Check CAPL syntax and semantics
- **Code Generation** – Generate CAPL code from templates or specifications

## Installation

You can run `capl_tools` instantly without installing it using `uvx`:

```bash
uvx capl-tools-lib scan my_file.can
```

Or install it globally as a tool:

```bash
uv tool install capl-tools-lib
```

Alternatively, install via pip:

```bash
pip install capl-tools-lib
```

## Project Structure

```
CAPL_Parser/
├── src/capl_tools_lib/
│   ├── cli.py          # Command Line Interface logic
│   ├── file_manager.py # File I/O and persistence
│   ├── processor.py    # High-level orchestration (Facade)
│   ├── editor.py       # Code manipulation utilities
│   ├── elements.py     # CAPL AST element definitions
│   ├── scanner.py      # Lexical analysis
│   └── common.py       # Shared utilities
├── tests/
│   ├── dev_script.py   # Development testing
│   └── data/
│       └── sample.can  # Sample CAPL file
└── README.md
```

## CLI Usage

Once installed, you can use the `capl_tools` command directly from your terminal.

### Basic Commands

```bash
# Show help
capl_tools --help

# Scan a file and show table of elements
capl_tools scan path/to/your_file.can

# Scan and output in machine-readable JSON (AI-Agent Ready)
capl_tools scan path/to/your_file.can --json

# Scan and output in token-efficient TOON format (Optimized for LLMs)
capl_tools scan path/to/your_file.can --toon

# Fetch raw code of a specific element (Surgical Context)
capl_tools get path/to/your_file.can MyFunction --type Function

# Insert code using semantic anchoring
capl_tools insert path/to/your_file.can --location after:MyFunction --source snippet.can --type TestCase

# Remove a specific element by name and type
capl_tools remove path/to/your_file.can --type TestCase --name "DeprecatedTest"

# Remove a specific test group
capl_tools remove-group path/to/your_file.can "MyTestGroup"
```

> **Tip:** If you don't want to install the package, you can run any command instantly using `uvx`:
> `uvx capl-tools-lib scan sample.can`

### Available Commands

- `scan`: List all detected elements. Supports `--json` and `--toon` (Token-Oriented Object Notation) for automation and LLM efficiency.
- `get`: Extract the raw code of a specific element (TestCase, Function, etc.).
- `insert`: Surgically inject code using semantic anchors (`after:<name>`, `section:<group>`, `line:<num>`).
- `remove`: Delete a specific element by type and name.
- `remove-group`: Remove all test cases belonging to a specific test group.

## Library Usage

### Scanning a File

```python
from pathlib import Path
from capl_tools_lib.processor import CaplProcessor

# 1. Initialize Processor
file_path = Path("tests/data/sample.can")
processor = CaplProcessor(file_path)

# 2. Scan for elements
elements = processor.scan()

from capl_tools_lib.elements import TestCase

for el in elements:
    detail = f" (Group: {el.group_name})" if isinstance(el, TestCase) else ""
    print(f"{el.__class__.__name__}: {el.name}{detail} (Lines {el.start_line}-{el.end_line})")
```

## Architecture

**CLI** → **Processor** → (**Scanner**, **Editor**, **FileManager**)

- `cli.py` – Entry point for terminal commands.
- `processor.py` – Orchestrates scanning, editing, and file management.
- `file_manager.py` – Handles file reading, writing, and backups.
- `scanner.py` – Extracts CAPL elements.
- `editor.py` – Manages in-memory string manipulation.
- `elements.py` – Defines the AST elements.


## Logging

The library includes a flexible logging system that can be configured in `src/capl_tools_lib/common.py`.

### Configuration

Open `src/capl_tools_lib/common.py` to adjust settings:

- **ENABLE_LOGGING**: Master switch to enable/disable all output.
- **DEFAULT_LEVEL**: Default level (e.g., `logging.WARNING`) for all modules.
- **MODULE_CONFIG**: Dictionary to enable specific logging levels for individual files (e.g., `{"capl_tools_lib.scanner": logging.DEBUG}`).

### Usage in Code

```python
from .common import get_logger

logger = get_logger(__name__)

logger.debug("Debug information")
logger.warning("Something might be wrong")
```

## Requirements

- Python 3.11+

## Testing
```powershell
# Run the group detection tests
uv run pytest tests/test_group_scanning.py

# Run tests with coverage report
 uv run pytest --cov=capl_tools_lib --cov-report=term-missing
```

## Development with uv

This project uses `uv` for lightning-fast Python package and environment management.

### 1. Initialize and Sync the Environment
Run this in your root directory (`CAPL_Parser`). This command will create the `uv.lock` file and the `.venv` folder.

```powershell
# This reads your pyproject.toml and sets up the virtual environment
uv sync
```

### 2. Adding Dependencies
If you need libraries for your parser (like `lark`, `ply`, or `regex`), add them using:

```powershell
uv add lark
```

### 3. How to use your package in scripts
Because the project uses a `src` layout with `tool.uv.package = true`, `uv` installs the package in editable mode by default. In your scripts, you can simply write:

```python
from capl_tools_lib.processor import CaplProcessor
```

## Versioning

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html). For a detailed list of changes, please refer to the [CHANGELOG.md](CHANGELOG.md).

## Contributing

Contributions are welcome! Please submit issues and pull requests.

## Support

For issues and questions, please open an issue on the repository.