# CAPL Tools Library Documentation

## CLI Documentation (cli.py)

### Overview
The `cli.py` module provides a Command Line Interface (CLI) for the library using `Typer`. It serves as the main entry point for users interacting with the tool via the terminal.

### Configuration
The CLI is registered in `pyproject.toml` under `[project.scripts]`:
```toml
[project.scripts]
capl-tools = "capl_tools_lib.cli:main"
```

### Instructions
- When helping me with this repo, always ensure commit messages follow the Conventional Commits specification (e.g., feat:, fix:, docs:, chore:). Before suggesting a release, remind me to run uv run cz bump to handle versioning and changelog generation

- When Adding/Removing commands from cli.py make sure to Update README.md Commands section.

---

## CaplProcessor Class

### Overview
The `CaplProcessor` is a high-level facade that orchestrates the `CaplFileManager`, `CaplScanner`, and `CaplEditor`. It simplifies common workflows like scanning, modifying, and saving CAPL files.

### Usage
```python
from pathlib import Path
from capl_tools_lib.processor import CaplProcessor

# Initialize
processor = CaplProcessor(Path("test.can"))

# Scan
elements = processor.scan()

# Modify
processor.remove_test_group("DeprecatedTests")

# Save
processor.save(backup=True)
```

---

## CaplScanner Class

### Overview
The `CaplScanner` parses CAPL files to identify constructs like includes, variables, handlers, functions, and test cases.

### Usage
```python
from capl_tools_lib.file_manager import CaplFileManager
from capl_tools_lib.scanner import CaplScanner

file_manager = CaplFileManager(Path("path/to/file.can"))
scanner = CaplScanner(file_manager)

# Scan for all supported elements
all_elements = scanner.scan_all()
```

### Scanning Strategies
(Same as before: IncludesScanner, VariablesScanner, HandlerScanner, TestCaseScanner, FunctionScanner)

---

## CaplEditor Class

### Overview
The `CaplEditor` class handles **in-memory** modification of CAPL file content. It strictly follows the Single Responsibility Principle by focusing only on string manipulation. File persistence is handled by `CaplFileManager` (or via `CaplProcessor`).

### Usage

#### Basic Setup
```python
from capl_tools_lib.file_manager import CaplFileManager
from capl_tools_lib.editor import CaplEditor

file_manager = CaplFileManager(Path("path/to/file.can"))
editor = CaplEditor(file_manager)
```

#### Removing Elements
```python
editor.remove_element(element)
editor.remove_elements([el1, el2])
```

#### Inserting/Replacing
```python
editor.insert_element(10, ["void func() {}"])
editor.replace_element(element, ["void new_impl() {}"])
```

#### Getting Modified Content
```python
# Get the modified lines to save them later
modified_lines = editor.get_lines()
```

---

## CaplFileManager Class

### Overview
The `CaplFileManager` class handles low-level file operations: reading, writing, and creating backups.

### Usage
```python
from capl_tools_lib.file_manager import CaplFileManager

file_manager = CaplFileManager(Path("file.can"))

# Access original lines
lines = file_manager.lines

# Save changes with backup
new_lines = ["// modified content"]
file_manager.save_file(target_path=Path("file.can"), lines=new_lines, backup=True)
```

### Key Features
- Reads CAPL files (cp1252 encoding)
- `save_file()`: Writes content to disk, automatically creating `.bak` files if requested.
- `strip_comments()`: Utility to get clean code lines.

---


## Notes
- The _dirty Flag Sync
Your CaplProcessor logic for the _dirty flag is excellent.

- dont foregt to update CHANGELOG.md when creating new tag.

Reminder: Whenever you add a new "Edit" feature (like insert_test_case), remember to set self._dirty = True so the Scanner knows the line numbers have shifted before the next scan().

## Development Environment Setup

### Critical Configuration Rules

#### 1. Build System Configuration
**DO NOT modify the build system configuration unless absolutely necessary:**
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

#### 2. Package Management
**ALWAYS use uv commands:**
```bash
uv run capl_tools --help
```
