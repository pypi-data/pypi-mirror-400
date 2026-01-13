from pathlib import Path
from typing import List, Optional, Dict, Any, Type

from capl_tools_lib.common import get_logger
from capl_tools_lib.file_manager import CaplFileManager
from capl_tools_lib.scanner import CaplScanner
from capl_tools_lib.editor import CaplEditor
from capl_tools_lib.elements import CAPLElement, TestCase

logger = get_logger(__name__)

class CaplProcessor:
    """
    High-level facade for processing CAPL files.
    Coordinates FileManager, Scanner, and Editor to perform complex operations.
    Implements the Facade pattern to simplify interactions with the CAPL toolchain.
    """
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.file_manager = CaplFileManager(file_path)
        self.editor = CaplEditor(self.file_manager)
        self.scanner = CaplScanner(self.file_manager)
        self._elements: Optional[List[CAPLElement]] = None
        self._dirty = False # Tracks if file has been modified since last scan

    def scan(self, force_refresh: bool = False) -> List[CAPLElement]:
        """
        Scans the file for elements. 
        Automatically syncs scanner with editor changes if needed.
        """
        if self._dirty:
            # Sync FileManager with Editor content so Scanner sees changes
            # Note: Scanner reads file_manager.lines
            self.file_manager.lines = list(self.editor.get_lines())
            force_refresh = True
            self._dirty = False

        if self._elements is None or force_refresh:
            self._elements = self.scanner.scan_all()
        
        return self._elements

    def get_stats(self) -> Dict[str, int]:
        """Returns a count of each element type."""
        elements = self.scan()
        from collections import Counter
        return dict(Counter(el.__class__.__name__ for el in elements))

    def remove_test_group(self, group_name: str) -> int:
        """
        Removes all test cases belonging to the specified group.
        Returns the number of test cases removed.
        """
        # Ensure we have fresh elements (will sync if dirty)
        elements = self.scan()
        
        to_remove = [
            el for el in elements 
            if isinstance(el, TestCase) and el.group_name == group_name
        ]
        
        if not to_remove:
            return 0
            
        logger.info(f"Processor removing {len(to_remove)} test cases from group '{group_name}'")
        self.editor.remove_elements(to_remove)
        
        # Mark as dirty so next scan re-reads from editor
        self._dirty = True
        self._elements = None 
        
        return len(to_remove)

    def save(self, output_path: Optional[Path] = None, backup: bool = True) -> None:
        """Saves changes to disk."""
        target = output_path if output_path else self.file_manager.file_path
        lines = self.editor.get_lines()
        self.file_manager.save_file(target, lines, backup=backup)

    def reload(self) -> None:
        """Reloads the file from disk, discarding unsaved changes."""
        self.editor.reset()
        self.file_manager._read_file() # Re-read from disk
        self._dirty = False
        self._elements = None
