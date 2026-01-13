import os
from pathlib import Path
from capl_tools_lib.file_manager import CaplFileManager
from capl_tools_lib.scanner import CaplScanner
from capl_tools_lib.common import MODULE_CONFIG
import logging

# Enable debug logging for the scanner to see strategy progress
MODULE_CONFIG["capl_tools_lib.scanner"] = logging.DEBUG

def main():
    # Path to the sample file
    sample_path = Path(__file__).parent / "data" / "sample_group.can"
    
    if not sample_path.exists():
        print(f"Error: Could not find sample file at {sample_path}")
        return

    print(f"--- Scanning file: {sample_path} ---")
    
    # Initialize File Manager
    file_manager = CaplFileManager(sample_path)
    
    # Initialize Scanner
    scanner = CaplScanner(file_manager)
    
    # Perform scan
    elements = scanner.scan_all()
    
    print(f"\nFound {len(elements)} elements:\n")
    
    # Group elements by type for summary
    summary = {}
    for el in elements:
        type_name = el.__class__.__name__
        summary[type_name] = summary.get(type_name, 0) + 1
        
        # Print details for each element
        line_range = f"L{el.start_line + 1}-{el.end_line + 1}"
        
        # Build the detail string
        sig = getattr(el, 'signature', None) or getattr(el, 'name', 'Unknown')
        
        # Add group info for TestCases
        from capl_tools_lib.elements import TestCase
        if isinstance(el, TestCase):
            sig += f" [Group: {el.group_name}]"
            
        print(f"[{type_name:12}] {line_range:10} | {sig}")

    print("\n--- Summary ---")
    for type_name, count in summary.items():
        print(f"{type_name}: {count}")

if __name__ == "__main__":
    main()
