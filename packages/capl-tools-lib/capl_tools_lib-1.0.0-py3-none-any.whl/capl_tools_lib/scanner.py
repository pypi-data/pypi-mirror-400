import re
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Type
from capl_tools_lib.file_manager import CaplFileManager
from capl_tools_lib.elements import CAPLElement, TestCase, Handler, Function, TestFunction, CaplInclude, CaplVariable
from capl_tools_lib.common import get_logger

logger = get_logger(__name__)

class CaplScanningStrategy(ABC):
    """ Base class for CAPL scanning strategies."""
    
    @abstractmethod
    def scan(self, file_manager: CaplFileManager) -> List[CAPLElement]:
        """ Scan the file and return a list of discovered elements. """
        pass

    def find_block_end(self, lines: List[str], start_line_idx: int) -> int:
        """ 
        Finds the closing brace '}' for a block starting at start_line_idx. 
        Returns the index of the line containing the closing brace.
        """
        open_braces = 0
        found_first_brace = False
        
        for i in range(start_line_idx, len(lines)):
            line = lines[i]
            
            # Simple brace counting; ideally ignores comments/strings
            # Remove comments for brace counting purposes
            clean_line = re.sub(r'//.*', '', line)
            clean_line = re.sub(r'/\*.*?\*/', '', clean_line) 
            
            open_braces += clean_line.count('{')
            open_braces -= clean_line.count('}')
            
            if '{' in clean_line:
                found_first_brace = True
            
            if found_first_brace and open_braces == 0:
                return i
                
        return start_line_idx # Fallback if no block found

class VariablesScanner(CaplScanningStrategy):
    PATTERN = re.compile(r'^\s*variables\s*\{')

    def scan(self, file_manager: CaplFileManager) -> List[CAPLElement]:
        elements = []
        lines = file_manager.lines
        
        for i, line in enumerate(lines):
            if self.PATTERN.match(line):
                end_line = self.find_block_end(lines, i)
                elements.append(CaplVariable(
                    start_line=i,
                    end_line=end_line
                ))
        return elements

class IncludesScanner(CaplScanningStrategy):
    PATTERN = re.compile(r'^\s*includes\s*\{')
    INCLUDE_PATTERN = re.compile(r'#include\s*[<"]([^>"]+)[>"]')

    def scan(self, file_manager: CaplFileManager) -> List[CAPLElement]:
        elements = []
        lines = file_manager.lines
        
        for i, line in enumerate(lines):
            if self.PATTERN.match(line):
                end_line = self.find_block_end(lines, i)
                
                # Extract included files
                content_lines = lines[i:end_line+1]
                content = "".join(content_lines)
                matches = self.INCLUDE_PATTERN.findall(content)
                
                elements.append(CaplInclude(
                    included_files=matches,
                    start_line=i,
                    end_line=end_line
                ))
        return elements

class HandlerScanner(CaplScanningStrategy):
    # Regex for 'on event_type condition'
    # e.g., 'on message 0x123', 'on timer t1', 'on key *'
    PATTERN = re.compile(r'^\s*on\s+(\w+)\s+(.+?)\s*(?:\{|$)')

    def scan(self, file_manager: CaplFileManager) -> List[CAPLElement]:
        elements = []
        lines = file_manager.lines
        
        for i, line in enumerate(lines):
            match = self.PATTERN.match(line)
            if match:
                event_type = match.group(1)
                condition = match.group(2).strip()
                
                end_line = self.find_block_end(lines, i)
                
                elements.append(Handler(
                    name=f"on {event_type} {condition}",
                    event_type=event_type,
                    condition=condition,
                    start_line=i,
                    end_line=end_line
                ))
        return elements

class TestCaseScanner(CaplScanningStrategy):
    """ Scans for TestCases and identifies their group association. """
    PATTERN = re.compile(r'^\s*testcase\s+(\w+)\s*\(')
    GROUP_PATTERN = re.compile(r'(?:InitializeTestGroup|CreateTestGroup)\s*\(\s*"([^"]+)"\s*\)')

    def scan(self, file_manager: CaplFileManager) -> List[CAPLElement]:
        elements = []
        lines = file_manager.lines
        current_group = "Default"

        for i, line in enumerate(lines):
            match = self.PATTERN.match(line)
            if match:
                end_line = self.find_block_end(lines, i)
                
                # Check for group initialization inside the testcase body
                body_lines = lines[i:end_line+1]
                body_content = "".join(body_lines)
                
                group_match = self.GROUP_PATTERN.search(body_content)
                if group_match:
                    current_group = group_match.group(1)
                
                elements.append(TestCase(
                    name=match.group(1),
                    description="", 
                    start_line=i,
                    end_line=end_line,
                    group=current_group
                ))
        return elements

class FunctionScanner(CaplScanningStrategy):
    """ Scans for TestFunctions and regular Functions """
    
    # 1. Test Functions: testfunction Name(args)
    TF_PATTERN = re.compile(r'^\s*testfunction\s+(\w+)\s*\((.*?)\)')
    
    # 2. Regular Functions: void Name(args) or int Name(args)
    FUNC_PATTERN = re.compile(r'^\s*(void|int|byte|long|float|double|char|dword|word)\s+(\w+)\s*\((.*?)\)')

    def scan(self, file_manager: CaplFileManager) -> List[CAPLElement]:
        elements = []
        lines = file_manager.lines

        for i, line in enumerate(lines):
            # Check Test Function
            match_tf = self.TF_PATTERN.match(line)
            if match_tf:
                end_line = self.find_block_end(lines, i)
                params_str = match_tf.group(2)
                params = [p.strip() for p in params_str.split(',') if p.strip()]
                
                elements.append(TestFunction(
                    name=match_tf.group(1),
                    params=params,
                    start_line=i,
                    end_line=end_line
                ))
                continue

            # Check Regular Function
            match_func = self.FUNC_PATTERN.match(line)
            if match_func:
                end_line = self.find_block_end(lines, i)
                params_str = match_func.group(3)
                params = [p.strip() for p in params_str.split(',') if p.strip()]
                
                elements.append(Function(
                    name=match_func.group(2),
                    return_type=match_func.group(1),
                    parameters=params,
                    start_line=i,
                    end_line=end_line
                ))
                continue

        return elements

class CaplScanner:
    """ Main Scanner class that orchestrates all strategies. """
    
    def __init__(self, file_manager: CaplFileManager):
        self.file_manager = file_manager
        self.strategies: List[CaplScanningStrategy] = [
            IncludesScanner(),
            VariablesScanner(),
            HandlerScanner(),
            TestCaseScanner(),
            FunctionScanner()
        ]

    def scan_all(self) -> List[CAPLElement]:
        all_elements = []
        logger.info(f"Starting scan of {self.file_manager.file_path}")
        
        for strategy in self.strategies:
            found = strategy.scan(self.file_manager)
            all_elements.extend(found)
            logger.debug(f"Strategy {strategy.__class__.__name__} found {len(found)} elements")
            
        # Sort elements by line number
        all_elements.sort(key=lambda x: x.start_line)
        return all_elements