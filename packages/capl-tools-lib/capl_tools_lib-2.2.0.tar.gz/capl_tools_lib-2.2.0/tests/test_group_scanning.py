import pytest
from pathlib import Path
from capl_tools_lib.file_manager import CaplFileManager
from capl_tools_lib.scanner import CaplScanner
from capl_tools_lib.elements import TestCase

# Fixture to provide the sample file path
@pytest.fixture
def sample_file_path():
    """Return the path to the sample_group.can file."""
    path = Path(__file__).parent / "data" / "sample_group.can"
    if not path.exists():
        pytest.fail(f"Test data file not found at {path}")
    return path

# Fixture to initialize the scanner and perform the scan
@pytest.fixture
def scanned_elements(sample_file_path):
    """Scan the sample file and return all discovered elements."""
    file_manager = CaplFileManager(sample_file_path)
    scanner = CaplScanner(file_manager)
    return scanner.scan_all()

# Fixture to filter only TestCases from scanned elements
@pytest.fixture
def test_cases(scanned_elements):
    """Filter and return only TestCase objects from scanned elements."""
    return [e for e in scanned_elements if isinstance(e, TestCase)]

class TestGroupScanning:
    """Tests for CAPL test group detection logic."""

    def test_total_test_cases_found(self, test_cases):
        """Verify the correct number of test cases are found."""
        assert len(test_cases) == 9

    @pytest.mark.parametrize("tc_index, expected_name, expected_group, expected_have_group", [
        (0, "PreInitTest", "Default", False),
        (1, "ChassisGroupMarker", "Chassis_Control_Tests", True),
        (2, "TC_Chassis_Brake", "Chassis_Control_Tests", True),
        (3, "TC_Chassis_Steering", "Chassis_Control_Tests", True),
        (4, "TC_Chassis_Suspension", "Chassis_Control_Tests", True),
        (5, "EngineGroupMarker", "Engine_Control_Tests", True),
        (6, "TC_Engine_Start", "Engine_Control_Tests", True),
        (7, "TC_Engine_RPM", "Engine_Control_Tests", True),
        (8, "CleanupTest", "Engine_Control_Tests", True),
    ])
    def test_test_case_groups(self, test_cases, tc_index, expected_name, expected_group, expected_have_group):
        """
        Verify that each test case has the expected name, group, and have_group status.
        Uses parametrization to check all test cases defined in the sample file.
        """
        tc = test_cases[tc_index]
        
        # Verify Name
        assert tc.name == expected_name, \
            f"Test case at index {tc_index} should be named '{expected_name}', but was '{tc.name}'"
        
        # Verify Group Name
        assert tc.group_name == expected_group, \
            f"Test case '{tc.name}' should be in group '{expected_group}', but was in '{tc.group_name}'"
        
        # Verify have_group Flag
        assert tc.have_group == expected_have_group, \
            f"Test case '{tc.name}' have_group should be {expected_have_group}"

    def test_group_transition_logic(self, test_cases):
        """
        Explicitly test the transitions between groups to ensure statefulness.
        """
        # Transition 1: Default -> Chassis_Control_Tests
        assert test_cases[0].group_name == "Default"
        assert test_cases[1].group_name == "Chassis_Control_Tests"
        
        # Transition 2: Chassis_Control_Tests -> Engine_Control_Tests
        # Find index where transition happens (between Suspension and EngineMarker)
        chassis_last = next(tc for tc in test_cases if tc.name == "TC_Chassis_Suspension")
        engine_first = next(tc for tc in test_cases if tc.name == "EngineGroupMarker")
        
        assert chassis_last.group_name == "Chassis_Control_Tests"
        assert engine_first.group_name == "Engine_Control_Tests"
