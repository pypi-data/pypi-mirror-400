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
        
        # Use the editor to remove them
        # Note: We must remove in reverse order of line numbers to avoid index shifts
        # But your editor.remove_elements might handle this? 
        # If not, sort here:
        to_remove.sort(key=lambda x: x.start_line, reverse=True)
        self.editor.remove_elements(to_remove)
        
        # Mark as dirty so next scan re-reads from editor
        self._dirty = True
        self._elements = None 
        
        return len(to_remove)

    def remove_element(self, element_type: str, name: str) -> int:
        """
        Removes elements matching the type and name.
        Returns the number of elements removed.
        """
        # Ensure we have fresh elements (will sync if dirty)
        elements = self.scan()
        
        to_remove = [
            el for el in elements 
            if el.__class__.__name__ == element_type and el.name == name
        ]
        
        if not to_remove:
            return 0
            
        logger.info(f"Processor removing {len(to_remove)} elements of type '{element_type}' with name '{name}'")
        
        # Use the editor to remove them
        # Note: We must remove in reverse order of line numbers to avoid index shifts
        # But your editor.remove_elements might handle this? 
        # If not, sort here:
        to_remove.sort(key=lambda x: x.start_line, reverse=True)
        self.editor.remove_elements(to_remove)
        
        # Mark as dirty so next scan re-reads from editor
        self._dirty = True
        self._elements = None 
        
        return len(to_remove)

    def get_element_code(self, element_type: str, name: str) -> Optional[str]:
        """
        Returns the raw code of the specified element as a string.
        """
        elements = self.scan()
        target = next((el for el in elements if el.__class__.__name__ == element_type and el.name == name), None)
        
        if not target:
            return None

        lines = self.editor.get_lines()
        # target.start_line and target.end_line are 0-indexed inclusive
        element_lines = lines[target.start_line : target.end_line + 1]
        return "".join(element_lines)

    def insert(self, location: str, code: str, element_type: Optional[str] = None) -> int:
        """
        Inserts code based on a semantic location anchor.
        Returns the line number where it was inserted.
        """
        elements = self.scan()
        target_line = -1

        if location.startswith("after:"):
            name = location.split(":", 1)[1]
            target = next((el for el in elements if el.name == name), None)
            if target:
                target_line = target.end_line + 1
            else:
                raise ValueError(f"Anchor element '{name}' not found.")

        elif location.startswith("line:"):
            target_line = int(location.split(":", 1)[1])

        elif location.startswith("section:"):
            section_name = location.split(":", 1)[1]
            from capl_tools_lib.elements import CaplInclude, CaplVariable, TestCase
            
            if section_name.lower() == "includes":
                target = next((el for el in elements if isinstance(el, CaplInclude)), None)
                target_line = target.end_line + 1 if target else 0
            elif section_name.lower() == "variables":
                target = next((el for el in elements if isinstance(el, CaplVariable)), None)
                target_line = target.end_line + 1 if target else 0
            else:
                # Assume section_name is a Test Group name
                group_elements = [el for el in elements if isinstance(el, TestCase) and el.group_name == section_name]
                if group_elements:
                    # Insert after the last test case of the group
                    target_line = group_elements[-1].end_line + 1
                else:
                    raise ValueError(f"Section or Group '{section_name}' not found.")
        
        if target_line == -1:
            raise ValueError(f"Could not resolve location: {location}")

        # Basic validation if element_type is provided (could be expanded)
        if element_type == "TestCase" and "testcase" not in code.lower():
            logger.warning("Inserting a TestCase but 'testcase' keyword not found in code.")

        # Ensure code ends with a newline and has proper padding
        if not code.endswith("\n"):
            code += "\n"
        
        # Split into lines keeping the newlines
        lines_to_insert = code.splitlines(keepends=True)
        
        # Add a leading newline for spacing if inserting in middle of file
        if target_line > 0:
            lines_to_insert.insert(0, "\n")

        self.editor.insert_lines(target_line, lines_to_insert)
        self._dirty = True
        self._elements = None
        return target_line

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
