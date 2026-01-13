from pathlib import Path
from typing import List, Dict, Optional

# Update these to include the package name
from capl_tools_lib.common import get_logger
from capl_tools_lib.file_manager import CaplFileManager
from capl_tools_lib.elements import CAPLElement, TestCase
logger = get_logger(__name__)


class CaplEditor:
    """ 
    Handles modification of CAPL file content, including deleting, inserting and replacing blocks
    """
    def __init__(self, file_mngr: Optional[CaplFileManager] = None, lines: Optional[List[str]] = None) -> None:
        self.file_mngr = file_mngr
        if lines is not None:
            self._current_lines = list(lines)
        elif file_mngr is not None:
            self._current_lines = list(file_mngr.lines)
        else:
            raise ValueError("Either file_mngr or lines must be provided to CaplEditor")
            
        logger.debug("CaplEditor initialized")

    def get_lines(self) -> List[str]:
        """ Returns the current state of the modified lines. """
        return self._current_lines
    
    def _get_modified_lines(self) -> List[str]:
        return self._current_lines
    
    def delete_lines(self, start:int, end:int) -> None:
        """ Deletes a range of lines (0-indexed, inclusive) """
        if start < 0 or end > len(self._current_lines) or start >= end:
            logger.error(f"Invalid line range for deletion: {start} to {end}")
            raise ValueError(f"Invalid line range: {start} to {end}")
        logger.info(f"Deleting lines {start} to {end}")
        del self._current_lines[start:end]

    def insert_lines(self, position:int, lines:List[str]) -> None:
        """ Inserts lines at a specific position (0-indexed) """
        if position < 0 or position > len(self._current_lines):
            logger.error(f"Invalid position for insertion: {position}")
            raise ValueError(f"Invalid position: {position}")
        logger.info(f"Inserting {len(lines)} lines at position {position}")
        self._current_lines[position:position] = lines

    def replace_lines(self, start:int, end:int, lines:List[str]) -> None:
        """ Replaces a range of lines (0-indexed, inclusive) """
        logger.info(f"Replacing lines {start} to {end} with {len(lines)} new lines")
        self.delete_lines(start, end)
        self.insert_lines(start, lines)

    def remove_elements(self, elements: List[CAPLElement]) -> None:
        """
        Removes multiple CAPL elements from the file
        
        Args:
            elements: List of CAPLElement objects to remove
        """
        # Sort elements by start line descending to avoid messing up indices
        elements_sorted = sorted(elements, key=lambda el: el.start_line, reverse=True)
        for el in elements_sorted:
            logger.info(f"Removing element {el.name} at lines {el.start_line}-{el.end_line}")
            # end_line is inclusive, so add 1 to make it exclusive for delete_lines
            self.delete_lines(el.start_line, el.end_line + 1)

    def remove_element(self, element: CAPLElement) -> None:
        """
        Removes a single CAPL element from the file
        
        Args:
            element: CAPLElement object to remove
        """
        self.remove_elements([element])

    def insert_element(self, position: int, element_lines: List[str]) -> None:
        """
        Inserts a new element at the specified position
        
        Args:
            position: Line position to insert at (0-indexed)
            element_lines: Lines of code for the element
        """
        self.insert_lines(position, element_lines)

    def reset(self) -> None:
        """Resets all changes, reverting to the original file content."""
        self._current_lines = list(self.file_mngr.lines)
        logger.info("Reset editor content to original state")