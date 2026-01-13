import sys
from pathlib import Path
from capl_tools_lib.file_manager import CaplFileManager
from capl_tools_lib.scanner import CaplScanner
from capl_tools_lib.elements import TestCase

def main():
    # Path to the sample file
    sample_path = Path(__file__).parent / "data" / "sample_group.can"
    
    if not sample_path.exists():
        print(f"Error: Could not find sample file at {sample_path}")
        return

    print(f"--- Scanning file: {sample_path} ---")
    
    file_manager = CaplFileManager(sample_path)
    scanner = CaplScanner(file_manager)
    elements = scanner.scan_all()
    
    # Filter only TestCases
    test_cases = [e for e in elements if isinstance(e, TestCase)]
    
    print(f"\nFound {len(test_cases)} TestCases:\n")
    print(f"{ 'TestCase Name':<25} | { 'Group Name':<25} | { 'Have Group':<10}")
    print("-" * 65)
    
    for tc in test_cases:
        print(f"{tc.name:<25} | {tc.group_name:<25} | {str(tc.have_group):<10}")

    # Assertions
    expected_groups = [
        ("PreInitTest", "Default"),
        ("ChassisGroupMarker", "Chassis_Control_Tests"),
        ("TC_Chassis_Brake", "Chassis_Control_Tests"),
        ("TC_Chassis_Steering", "Chassis_Control_Tests"),
        ("TC_Chassis_Suspension", "Chassis_Control_Tests"),
        ("EngineGroupMarker", "Engine_Control_Tests"),
        ("TC_Engine_Start", "Engine_Control_Tests"),
        ("TC_Engine_RPM", "Engine_Control_Tests"),
        ("CleanupTest", "Engine_Control_Tests"),
    ]

    print("\n--- Verifying Groups ---")
    for i, (expected_name, expected_group) in enumerate(expected_groups):
        tc = test_cases[i]
        status = "PASS" if tc.group_name == expected_group else "FAIL"
        print(f"[{status}] {tc.name}: expected '{expected_group}', got '{tc.group_name}'")

if __name__ == "__main__":
    main()
