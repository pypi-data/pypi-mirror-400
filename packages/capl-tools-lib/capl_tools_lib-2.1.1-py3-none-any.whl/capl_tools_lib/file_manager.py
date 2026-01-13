import re
import shutil
from pathlib import Path
from capl_tools_lib.common import get_logger
TEST_STATUS_PASS = 1
TEST_STATUS_FAIL = 0
TEST_STATUS_SKIPPED = -2
TEST_STATUS_INCONCLUSIVE = -3

logger = get_logger(__name__)

class CaplFileManager:
    """ 
    Handles Low Level file operations for CAPL files, reading, writing, and managing file paths.
    """
    def __init__(self, file_path: Path):
        self.file_path: Path = file_path
        self.lines: list[str] = []

        logger.debug(f"Initialized CaplFileManager for {file_path}")
        self._read_file()

    def _read_file(self):
        try:
            with self.file_path.open('r', encoding='cp1252') as f:
                self.lines = f.readlines()
                logger.debug(f"Successfully read {len(self.lines)} lines from {self.file_path}")
        except Exception as e:
            logger.error(f"Error reading {self.file_path}: {e}")
            raise IOError(f"Could not read file {self.file_path}: {e}")

    def get_lines(self, start: int, end: int) -> list[str]:
        if start < 0 or end > len(self.lines) or start >= end:
            logger.error(f"Invalid line range requested: {start} to {end}")
            raise ValueError(f"Invalid line range: {start} to {end}")
        
        logger.debug(f"Retrieving lines {start} to {end} from {self.file_path}")

        return self.lines[start:end]
    
    def write_lines(self, output_path: Path, lines: list[str]):
        if not output_path.parent.exists():
            output_path.parent.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created directories for {output_path.parent}")

        try:
            with output_path.open('w', encoding='cp1252') as f:
                f.writelines(lines)
                logger.info(f"Successfully wrote {len(lines)} lines to {output_path}")
        except Exception as e:
            logger.error(f"Error writing to {output_path}: {e}")
            raise IOError(f"Could not write to file {output_path}: {e}")

    def save_file(self, target_path: Path, lines: list[str], backup: bool = True) -> None:
        """
        Saves lines to the target path, optionally creating a backup if overwriting.
        """
        if backup and target_path.exists():
            backup_path = target_path.with_suffix(target_path.suffix + ".bak")
            try:
                shutil.copy2(target_path, backup_path)
                logger.info(f"Created backup at {backup_path}")
            except Exception as e:
                logger.warning(f"Failed to create backup: {e}")

        self.write_lines(target_path, lines)
        
    def strip_comments(self) -> list[str]:
        """ Return lines with // comments stripped out. """
        stripped_lines = []
        for line in self.lines:
            stripped_line = re.sub(r'//.*','', line).strip()
            if stripped_line:
                stripped_lines.append(stripped_line)
        logger.debug(f"stripped {len(self.lines) - len(stripped_lines)} comments from {self.file_path}")
        return stripped_lines