from enum import Enum
from typing import List, Optional, Any

class CAPLElement:
    def __init__(self, name: str, start_line: int, end_line: int, signature: Optional[str] = None):
        self.name = name
        self.start_line = start_line   # 0-indexed
        self.end_line   = end_line     # 0-indexed
        self.signature  = signature
    
    @property
    def display_name(self) -> str:
        """Returns a human-readable name for the element."""
        return self.name

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name='{self.name}' lines={self.start_line}-{self.end_line}>"
    
    def get_line_range(self) -> tuple[int, int]:
        return (self.start_line, self.end_line)
    
class TestCase(CAPLElement):
    # Prevent pytest from collecting this as a test class
    __test__ = False

    def __init__(self, name: str, description: str, start_line: int, end_line: int, group: Optional[str] = None):
        super().__init__(name, start_line, end_line, signature=f"testcase {name}()")
        self.description: str     = description
        
        # Group Attributes
        self.group_name: str = group if group else "Default"
        self.have_group: bool = group is not None and group != "Default"

    @property
    def display_name(self) -> str:
        if self.have_group:
            return f"{self.name} (Group: {self.group_name})"
        return self.name

    def __repr__(self) -> str:
        return f"<TestCase name='{self.name}' group='{self.group_name}' lines={self.start_line}-{self.end_line}>"


class Handler(CAPLElement):
    def __init__(self, name: str, event_type: str, condition: str, start_line: int, end_line: int, signature: Optional[str] = None):
        super().__init__(name, start_line, end_line, signature=signature or f"on {event_type} {condition}")
        self.event_type: str = event_type
        self.condition: str  = condition

    @property
    def display_name(self) -> str:
        return f"on {self.event_type} {self.condition}"

class Function(CAPLElement):
    def __init__(self, name: str, return_type: str, parameters: List[str], start_line: int, end_line: int, signature: Optional[str] = None):
        super().__init__(name, start_line, end_line, signature=signature or f"{return_type} {name}({', '.join(parameters)})")
        self.return_type: str     = return_type
        self.parameters: List[str] = parameters

    @property
    def display_name(self) -> str:
        return f"{self.return_type} {self.name}({', '.join(self.parameters)})"

    def __repr__(self) -> str:
        return f"<Function name='{self.name}' signature='{self.signature}' lines={self.start_line}-{self.end_line}>"

class TestFunction(CAPLElement):
    __test__ = False
    def __init__(self, name: str, params: List[str], start_line: int, end_line: int, signature: Optional[str] = None):
        super().__init__(name, start_line, end_line, signature=signature or f"testfunction {name}({', '.join(params)})")
        self.params: List[str] = params

    @property
    def display_name(self) -> str:
        return f"testfunction {self.name}({', '.join(self.params)})"

    def __repr__(self) -> str:
        return f"<TestFunction name='{self.name}' signature='{self.signature}' lines={self.start_line}-{self.end_line}>"
    
class CaplInclude(CAPLElement):
    def __init__(self, included_files: list[str], start_line: int, end_line: int):
        name = f"Includes ({len(included_files)} files)"
        super().__init__(name=name, start_line=start_line, end_line=end_line)
        self.included_files: list[str] = included_files

    @property
    def display_name(self) -> str:
         return f"Includes: {', '.join(self.included_files)}"

    def __repr__(self) -> str:
        return f"<CaplInclude files={len(self.included_files)} lines={self.start_line}-{self.end_line}>"

class CaplVariable(CAPLElement):
    def __init__(self,start_line: int, end_line: int):
        super().__init__(name="Variables", start_line=start_line, end_line=end_line,signature="variables {...}")

    def __repr__(self) -> str:
        return f"<CaplVariable lines={self.start_line}-{self.end_line}>"