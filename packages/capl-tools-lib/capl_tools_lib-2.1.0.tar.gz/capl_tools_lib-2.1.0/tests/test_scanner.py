"""
Tests for CAPL Scanner functionality
"""
import pytest
from pathlib import Path
from capl_tools_lib.file_manager import CaplFileManager
from capl_tools_lib.scanner import CaplScanner
from capl_tools_lib.elements import (
    CaplInclude, 
    CaplVariable, 
    Handler, 
    Function, 
    TestFunction, 
    TestCase,
    TestGroup
)


# Fixture for sample CAPL file path
@pytest.fixture
def sample_capl_file(tmp_path):
    """Creates a temporary CAPL file for testing"""
    content = '''includes {
    #include "common_lib.cin",
    #include "utils_lib.cin"
}

variables {
    int gCounter = 0;
    message EngineStatus msg1;
    msTimer tCyclic;
}

on start {
    write("Simulation Started");
    setTimer(tCyclic, 100);
}

on message EngineStatus {
    gCounter++;
    processData(this.RPM);
}

on timer tCyclic {
    setTimer(tCyclic, 100);
}

on someipSD *
{
    write("SomeIP Service Discovery Message Received");
}

on someipMessage 0x0012:0x1234:Notification
{
    write("SomeIP Message Received: 123456");
}


void processData(int value) {
    if(value > 3000) write("High RPM!");
}


testfunction testProcessData() {
    int testValue = 3500;
    processData(testValue);
}


testcase TC1_ProcessData()
{
    testProcessData();
}

testcase TC2_MessageHandling()
{
    EngineStatus testMsg;
    testMsg.RPM = 3200;
    write("Simulating EngineStatus Message with RPM: ", testMsg.RPM);
}

testcase Timer_StartTestSeries() {
  InitializeTestGroup("Chassis_Control_Tests");
}

testcase TC3_TimerFunctionality()
{
    write("Testing Timer Functionality");
}
'''
    file_path = tmp_path / "sample.can"
    file_path.write_text(content, encoding='utf-8')
    return file_path


@pytest.fixture
def file_manager(sample_capl_file):
    """Creates a CaplFileManager instance with the sample file"""
    return CaplFileManager(sample_capl_file)


@pytest.fixture
def scanner(file_manager):
    """Creates a CaplScanner instance with the file manager"""
    return CaplScanner(file_manager)


class TestCaplScannerInitialization:
    """Tests for scanner initialization"""
    
    def test_scanner_creates_successfully(self, file_manager):
        """Test that scanner initializes without errors"""
        scanner = CaplScanner(file_manager)
        assert scanner is not None
        assert scanner.file_manager == file_manager
    
    def test_scanner_with_nonexistent_file(self):
        """Test that file manager raises error for non-existent file"""
        with pytest.raises((FileNotFoundError, OSError)):
            CaplFileManager(Path("nonexistent_file.can"))
    
    def test_scanner_reads_file_content(self, file_manager):
        """Test that file manager reads file content"""
        assert len(file_manager.lines) > 0
        assert any("includes" in line for line in file_manager.lines)


class TestElementCounting:
    """Tests for counting different element types"""
    
    def test_total_element_count(self, scanner):
        """Test total number of elements found"""
        elements = scanner.scan_all()
        assert len(elements) == 14
    
    def test_include_count(self, scanner):
        """Test number of include blocks found"""
        elements = scanner.scan_all()
        includes = [e for e in elements if isinstance(e, CaplInclude)]
        assert len(includes) == 1
    
    def test_variable_count(self, scanner):
        """Test number of variable blocks found"""
        elements = scanner.scan_all()
        variables = [e for e in elements if isinstance(e, CaplVariable)]
        assert len(variables) == 1
    
    def test_handler_count(self, scanner):
        """Test number of handlers found"""
        elements = scanner.scan_all()
        handlers = [e for e in elements if isinstance(e, Handler)]
        assert len(handlers) == 5
    
    def test_function_count(self, scanner):
        """Test number of regular functions found"""
        elements = scanner.scan_all()
        functions = [e for e in elements if isinstance(e, Function)]
        assert len(functions) == 1
    
    def test_testfunction_count(self, scanner):
        """Test number of test functions found"""
        elements = scanner.scan_all()
        test_functions = [e for e in elements if isinstance(e, TestFunction)]
        assert len(test_functions) == 1
    
    def test_testcase_count(self, scanner):
        """Test number of test cases found"""
        elements = scanner.scan_all()
        test_cases = [e for e in elements if isinstance(e, TestCase)]
        assert len(test_cases) == 4

    def test_testgroup_count(self, scanner):
        """Test number of test groups found"""
        elements = scanner.scan_all()
        test_groups = [e for e in elements if isinstance(e, TestGroup)]
        assert len(test_groups) == 1


class TestElementDetails:
    """Tests for specific element details and properties"""
    
    def test_include_line_range(self, scanner):
        """Test that include block has correct line range"""
        elements = scanner.scan_all()
        includes = [e for e in elements if isinstance(e, CaplInclude)]
        assert len(includes) == 1
        include = includes[0]
        assert include.start_line == 0  # Line 1 in file = index 0
        assert include.end_line == 3    # Line 4 in file = index 3
    
    def test_variable_line_range(self, scanner):
        """Test that variable block has correct line range"""
        elements = scanner.scan_all()
        variables = [e for e in elements if isinstance(e, CaplVariable)]
        assert len(variables) == 1
        var_block = variables[0]
        assert var_block.start_line == 5   # Line 6 in file
        assert var_block.end_line == 9     # Line 10 in file
    
    def test_handler_signatures(self, scanner):
        """Test that handlers have correct signatures"""
        elements = scanner.scan_all()
        handlers = [e for e in elements if isinstance(e, Handler)]
        
        signatures = [h.signature for h in handlers]
        assert "on start {" in signatures
        assert "on message EngineStatus" in signatures
        assert "on timer tCyclic" in signatures
        assert "on someipSD *" in signatures
        assert "on someipMessage 0x0012:0x1234:Notification" in signatures
    
    def test_function_signature(self, scanner):
        """Test that function has correct signature"""
        elements = scanner.scan_all()
        functions = [e for e in elements if isinstance(e, Function)]
        assert len(functions) == 1
        func = functions[0]
        assert func.name == "processData"
        assert func.signature == "void processData(int value)"
    
    def test_testfunction_name(self, scanner):
        """Test that test function has correct name"""
        elements = scanner.scan_all()
        test_functions = [e for e in elements if isinstance(e, TestFunction)]
        assert len(test_functions) == 1
        test_func = test_functions[0]
        assert test_func.name == "testProcessData"
    
    def test_testcase_names(self, scanner):
        """Test that all test cases have correct names"""
        elements = scanner.scan_all()
        test_cases = [e for e in elements if isinstance(e, TestCase)]
        
        names = [tc.name for tc in test_cases]
        assert "TC1_ProcessData" in names
        assert "TC2_MessageHandling" in names
        assert "Timer_StartTestSeries" in names
        assert "TC3_TimerFunctionality" in names
    
    def test_testcase_line_ranges(self, scanner):
        """Test that test cases have correct line ranges"""
        elements = scanner.scan_all()
        test_cases = [e for e in elements if isinstance(e, TestCase)]
        
        # Find TC1_ProcessData
        tc1 = next(tc for tc in test_cases if tc.name == "TC1_ProcessData")
        assert tc1.start_line == 47  # Line 48
        assert tc1.end_line == 50    # Line 51


class TestElementOrdering:
    """Tests for element ordering in the file"""
    
    def test_elements_ordered_by_line_number(self, scanner):
        """Test that elements are returned in order of appearance"""
        elements = scanner.scan_all()
        line_numbers = [e.start_line for e in elements]
        assert line_numbers == sorted(line_numbers)
    
    def test_first_element_is_include(self, scanner):
        """Test that first element is the include block"""
        elements = scanner.scan_all()
        assert isinstance(elements[0], CaplInclude)
    
    def test_second_element_is_variables(self, scanner):
        """Test that second element is the variables block"""
        elements = scanner.scan_all()
        assert isinstance(elements[1], CaplVariable)


class TestEdgeCases:
    """Tests for edge cases and special scenarios"""
    
    def test_empty_file(self, tmp_path):
        """Test scanner behavior with empty file"""
        empty_file = tmp_path / "empty.can"
        empty_file.write_text("", encoding='utf-8')
        
        file_manager = CaplFileManager(empty_file)
        scanner = CaplScanner(file_manager)
        elements = scanner.scan_all()
        assert len(elements) == 0
    
    def test_file_with_only_comments(self, tmp_path):
        """Test scanner behavior with only comments"""
        comment_file = tmp_path / "comments.can"
        comment_file.write_text("""
// This is a comment
/* Multi-line
   comment */
        """, encoding='utf-8')
        
        file_manager = CaplFileManager(comment_file)
        scanner = CaplScanner(file_manager)
        elements = scanner.scan_all()
        assert len(elements) == 0
    
    def test_multiple_scans_return_same_results(self, scanner):
        """Test that scanning multiple times gives consistent results"""
        elements1 = scanner.scan_all()
        elements2 = scanner.scan_all()
        
        assert len(elements1) == len(elements2)
        for e1, e2 in zip(elements1, elements2):
            assert type(e1) == type(e2)
            assert e1.start_line == e2.start_line
            assert e1.end_line == e2.end_line


class TestGetMethods:
    """Tests for convenience getter methods if they exist"""
    
    def test_get_test_cases_method(self, file_manager):
        """Test get_test_cases method if it exists"""
        if hasattr(file_manager, 'get_test_cases'):
            test_cases = file_manager.get_test_cases()
            assert len(test_cases) == 4
            assert all(isinstance(tc, TestCase) for tc in test_cases)
    
    def test_get_functions_method(self, file_manager):
        """Test get_functions method if it exists"""
        if hasattr(file_manager, 'get_functions'):
            functions = file_manager.get_functions()
            assert len(functions) == 1
            assert all(isinstance(f, Function) for f in functions)
    
    def test_get_handlers_method(self, file_manager):
        """Test get_handlers method if it exists"""
        if hasattr(file_manager, 'get_handlers'):
            handlers = file_manager.get_handlers()
            assert len(handlers) == 5
            assert all(isinstance(h, Handler) for h in handlers)


class TestElementRepresentation:
    """Tests for element string representation"""
    
    def test_element_has_repr(self, scanner):
        """Test that elements have string representation"""
        elements = scanner.scan_all()
        for element in elements:
            repr_str = repr(element)
            assert repr_str is not None
            assert len(repr_str) > 0
    
    def test_element_repr_contains_line_info(self, scanner):
        """Test that repr includes line information"""
        elements = scanner.scan_all()
        for element in elements:
            repr_str = repr(element)
            assert "start_line" in repr_str or str(element.start_line) in repr_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])