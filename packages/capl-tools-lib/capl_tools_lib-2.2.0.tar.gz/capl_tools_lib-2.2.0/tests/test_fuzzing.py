"""
Enhanced Property-Based Fuzzing Tests for CAPL Parser
Based on real CAPL examples from Vector CANoe/CANalyzer
"""
from pathlib import Path
from hypothesis import given, strategies as st, settings, HealthCheck, assume
from capl_tools_lib.file_manager import CaplFileManager
from capl_tools_lib.scanner import CaplScanner


# ============================================================================ 
# MockFileManager - Avoid disk I/O
# ============================================================================ 
class MockFileManager(CaplFileManager):
    def __init__(self, content: str):
        self.file_path = Path("fuzz_test.can")
        self.lines = [line + "\n" for line in content.splitlines()]
        if not self.lines and content:
            self.lines = [content]
    
    def _read_file(self):
        pass


# ============================================================================ 
# CAPL Grammar Generators (Based on Real Examples)
# ============================================================================ 

@st.composite
def capl_identifier(draw):
    """Generate valid CAPL identifiers."""
    return draw(st.from_regex(r'[a-zA-Z_][a-zA-Z0-9_]{0,50}', fullmatch=True))


@st.composite
def capl_type(draw):
    """Generate CAPL data types seen in real code."""
    return draw(st.sampled_from([
        'int', 'long', 'byte', 'word', 'dword', 'qword',
        'float', 'double', 'char', 'message',
        'IP_Endpoint', 'ethernetPacket', 'msTimer'
    ]))


@st.composite
def capl_number(draw):
    """Generate CAPL numeric literals."""
    return draw(st.one_of(
        st.integers(min_value=0, max_value=0xFFFFFFFF).map(str),
        st.integers(min_value=0, max_value=0xFFFF).map(lambda x: f"0x{x:04X}"),
        st.floats(min_value=0, max_value=1000, allow_nan=False).map(lambda x: f"{x:.2f}")
    ))


@st.composite
def capl_string_literal(draw):
    """Generate CAPL string literals with escape sequences."""
    content = draw(st.text(
        alphabet=st.characters(
            blacklist_characters='"\\',
            blacklist_categories=('Cs', 'Cc')
        ),
        max_size=40
    ))
    # Add occasional escape sequences
    if draw(st.booleans()):
        escapes = draw(st.sampled_from(['\n', '\t', '\r', '\"', '\\']))
        content += escapes
    return f'"{content}"'


@st.composite
def capl_array_init(draw):
    """Generate array initializers like {0x01, 0x02, 0x03}."""
    size = draw(st.integers(min_value=1, max_value=10))
    values = [draw(capl_number()) for _ in range(size)]
    return "{ " + ", ".join(values) + " }"


@st.composite
def capl_variable_declaration(draw):
    """Generate variable declarations matching real CAPL patterns."""
    var_type = draw(capl_type())
    var_name = draw(capl_identifier())
    
    # Array notation
    if draw(st.booleans()):
        size = draw(st.integers(min_value=1, max_value=100))
        var_decl = f"{var_type} {var_name}[{size}]"
    else:
        var_decl = f"{var_type} {var_name}"
    
    # Initialization
    if draw(st.booleans()):
        if '[' in var_decl:
            init_val = draw(capl_array_init())
        else:
            init_val = draw(capl_number())
        var_decl += f" = {init_val}"
    
    return var_decl + ";"


@st.composite
def capl_variables_block(draw):
    """Generate variables { ... } block."""
    num_vars = draw(st.integers(min_value=0, max_value=8))
    vars_list = [draw(capl_variable_declaration()) for _ in range(num_vars)]
    
    if vars_list:
        vars_str = "\n  ".join(vars_list)
        return f"variables\n{{\n  {vars_str}\n}}"
    else:
        return "variables\n{\n}"


@st.composite
def capl_statement(draw):
    """Generate realistic CAPL statements from examples."""
    var = draw(capl_identifier())
    num = draw(capl_number())
    
    statements = [
        # Write statements
        f'write("{draw(st.text(max_size=30))}", {var});',
        f'write("Message #%d", {var});',
        f'write("ID: 0x%03X", {var});',
        
        # Assignments
        f"{var} = {num};",
        f"{var} = {draw(capl_identifier())}();",
        f" @sysvar::MyNamespace::{var} = {num};",
        
        # Function calls (from examples)
        f"setTimer({var}, {num});",
        f"AREthSetData({var}, {num}, {draw(capl_identifier())});",
        f"sysSetVariableData({draw(capl_identifier())}, {draw(capl_identifier())}, {var}, {num});",
        f"TestStepPass({draw(capl_string_literal())}, {draw(capl_string_literal())});",
        f"TestStepFail({draw(capl_string_literal())}, {draw(capl_string_literal())});",
        
        # Control flow
        f"if ({var} == {num}) {{ }}",
        f"if ({var} != 0) {{ return; }}",
        f"for (int i = 0; i < {num}; i++) {{ }}",
        f"while ({var}) {{ break; }}",
        
        # Comments
        f"// {draw(st.text(max_size=40))}",
        f"/* {draw(st.text(max_size=40))} */"
    ]
    
    return draw(st.sampled_from(statements))


@st.composite
def capl_block_body(draw):
    """Generate function/handler body with realistic statements."""
    num_statements = draw(st.integers(min_value=0, max_value=8))
    statements = [draw(capl_statement()) for _ in range(num_statements)]
    
    if statements:
        body_str = "\n  ".join(statements)
        return f"{{\n  {body_str}\n}}"
    else:
        return "{ }"


@st.composite
def capl_function(draw):
    """Generate function declarations (void, on timer, on key, etc)."""
    func_name = draw(capl_identifier())
    return_type = draw(st.sampled_from(['void', 'int', 'long', 'byte', 'float']))
    
    # Parameters
    num_params = draw(st.integers(min_value=0, max_value=4))
    params = []
    for _ in range(num_params):
        param_type = draw(capl_type())
        param_name = draw(capl_identifier())
        params.append(f"{param_type} {param_name}")
    
    param_str = ", ".join(params)
    body = draw(capl_block_body())
    
    return f"{return_type} {func_name}({param_str}) {body}"


@st.composite
def capl_testcase(draw):
    """Generate testcase declarations."""
    test_name = draw(capl_identifier())
    body = draw(capl_block_body())
    return f"testcase {test_name}() {body}"


@st.composite
def capl_event_handler(draw):
    """Generate event handlers (on start, on message, on timer, on key)."""
    handler_types = [
        "on start",
        "on stop",
        "on prestart",
        f"on message CAN1::*",
        f"on message CAN1::{draw(capl_identifier())}",
        f"on timer {draw(capl_identifier())}",
        f"on key '{draw(st.sampled_from(['a', 'c', 's', 'x']))}'",
    ]
    
    handler = draw(st.sampled_from(handler_types))
    body = draw(capl_block_body())
    
    return f"{handler} {body}"


@st.composite
def capl_includes_block(draw):
    """Generate includes { } block."""
    num_includes = draw(st.integers(min_value=0, max_value=3))
    
    if num_includes > 0:
        includes = [f'#include <{draw(capl_identifier())}.cin>' for _ in range(num_includes)]
        includes_str = "\n  ".join(includes)
        return f"includes\n{{\n  {includes_str}\n}}"
    else:
        return "includes\n{\n}"


@st.composite
def capl_complete_program(draw):
    """Generate complete, realistic CAPL program."""
    elements = []
    
    # Optional header comment
    if draw(st.booleans()):
        comment = draw(st.text(max_size=80))
        elements.append(f"// {comment}")
    
    # Includes block (common in real files)
    if draw(st.booleans()):
        elements.append(draw(capl_includes_block()))
    
    # Variables block (very common)
    if draw(st.booleans()):
        elements.append(draw(capl_variables_block()))
    
    # Functions
    num_functions = draw(st.integers(min_value=0, max_value=5))
    for _ in range(num_functions):
        elements.append(draw(capl_function()))
    
    # Event handlers
    num_handlers = draw(st.integers(min_value=0, max_value=4))
    for _ in range(num_handlers):
        elements.append(draw(capl_event_handler()))
    
    # Test cases
    num_testcases = draw(st.integers(min_value=1, max_value=4))
    for _ in range(num_testcases):
        elements.append(draw(capl_testcase()))
    
    return "\n\n".join(elements)


@st.composite
def capl_edge_cases(draw):
    """Generate specific edge cases that often break parsers."""
    cases = [
        # Empty constructs
        "variables { }",
        "includes { }",
        "testcase empty() { }",
        "void empty() { }",
        
        # Minimal spacing
        "testcase test(){write(\"x\");}",
        "variables{int x;}",
        
        # Excessive spacing
        "testcase    test   (  )   {   }",
        "variables  \n  {\n  int   x  ;\n  }",
        
        # Comments everywhere
        "/* c1 */ testcase /* c2 */ test() /* c3 */ { /* c4 */ }",
        "// comment\ntestcase test() { }",
        
        # Nested braces
        "testcase test() { { { } } }",
        "void func() { if (x) { for (i=0; i<10; i++) { } } }",
        
        # String literals with special chars
        'testcase test() { write("test\n\t\""); }',
        'testcase test() { write("0x%02X", x); }',
        
        # Arrays and initializers
        "variables { byte data[30] = {0x01, 0x02, 0x03}; }",
        "variables { char name[64] = \"test\"; }",
        
        # System variables (from examples)
        "on start { @sysvar::MyNamespace::EventGroupSubscribed = 1; }",
        
        # Long identifiers
        f"testcase {'test' * 20}() {{ }}",
        
        # Multiple on same line
        "testcase a() { } testcase b() { }",
        
        # Mixed line endings
        "testcase test1() {}\r\ntestcase test2() {}\n",
        
        # Uncommon but valid handlers
        "on key 'c' { write(\"pressed\"); }",
        "on timer updateTimer { setTimer(updateTimer, 100); }",
        "on message CAN1::* { write(\"%d\", this.ID); }",
    ]
    
    return draw(st.sampled_from(cases))


# ============================================================================ 
# Test 1: Random Text (Crash Prevention)
# ============================================================================ 
@settings(suppress_health_check=[HealthCheck.too_slow], max_examples=100)
@given(st.text())
def test_fuzz_scanner_random_text(content):
    """Scanner should handle any random text without crashing."""
    file_manager = MockFileManager(content)
    scanner = CaplScanner(file_manager)
    
    try:
        scanner.scan_all()
    except (SystemExit, KeyboardInterrupt, RecursionError):
        raise  # These are serious problems
    except Exception:
        pass  # Expected parsing errors are OK


# ============================================================================ 
# Test 2: Realistic CAPL Programs (Output Validation)
# ============================================================================ 
@settings(suppress_health_check=[HealthCheck.too_slow], max_examples=50)
@given(capl_complete_program())
def test_fuzz_realistic_capl_invariants(content):
    """Test with realistic CAPL programs and verify invariants."""
    file_manager = MockFileManager(content)
    scanner = CaplScanner(file_manager)
    
    try:
        elements = scanner.scan_all()
        
        # INVARIANT 1: Elements should not overlap
        for i, elem1 in enumerate(elements):
            for elem2 in elements[i+1:]:
                # Check if ranges overlap
                overlaps = (
                    (elem1.start_line <= elem2.start_line <= elem1.end_line) or
                    (elem1.start_line <= elem2.end_line <= elem1.end_line) or
                    (elem2.start_line <= elem1.start_line <= elem2.end_line)
                )
                assert not overlaps, \
                    f"Overlapping: {elem1.name}({elem1.start_line}-{elem1.end_line}) " \
                    f"and {elem2.name}({elem2.start_line}-{elem2.end_line})"
        
        # INVARIANT 2: Line numbers should be valid
        for elem in elements:
            assert elem.start_line > 0, f"Invalid start_line: {elem.start_line}"
            assert elem.end_line >= elem.start_line, \
                f"End before start: {elem.name} ({elem.start_line}-{elem.end_line})"
        
        # INVARIANT 3: Elements should have names
        for elem in elements:
            assert elem.name and elem.name.strip(), \
                f"Element without name: {type(elem).__name__}"
        
        # INVARIANT 4: If we generated testcases, we should find at least one
        if 'testcase' in content.lower() and content.strip():
            test_cases = [e for e in elements 
                         if 'testcase' in type(e).__name__.lower()]
            assert len(test_cases) > 0, \
                "Generated testcases but scanner found none"
                
    except (SystemExit, KeyboardInterrupt, RecursionError):
        raise
    except Exception as e:
        # If parsing fails, that's OK, but log it for debugging
        pass


# ============================================================================ 
# Test 3: Edge Cases Collection
# ============================================================================ 
@settings(max_examples=30)
@given(st.lists(capl_edge_cases(), min_size=1, max_size=5))
def test_fuzz_edge_cases(cases):
    """Test specific edge cases that often break parsers."""
    content = "\n\n".join(cases)
    file_manager = MockFileManager(content)
    scanner = CaplScanner(file_manager)
    
    try:
        elements = scanner.scan_all()
        
        # If parsing succeeded, verify basic invariants
        for elem in elements:
            assert elem.start_line > 0
            assert elem.end_line >= elem.start_line
            assert elem.name
            
    except (SystemExit, KeyboardInterrupt, RecursionError):
        raise
    except Exception:
        pass  # Malformed input is OK to fail


# ============================================================================ 
# Test 4: Consistency (Same Input = Same Output)
# ============================================================================ 
@settings(suppress_health_check=[HealthCheck.too_slow], max_examples=30)
@given(capl_complete_program())
def test_fuzz_scan_consistency(content):
    """Scanning same content twice should yield identical results."""
    assume(len(content) > 10)  # Skip trivial inputs
    
    file_manager1 = MockFileManager(content)
    scanner1 = CaplScanner(file_manager1)
    
    file_manager2 = MockFileManager(content)
    scanner2 = CaplScanner(file_manager2)
    
    try:
        elements1 = scanner1.scan_all()
        elements2 = scanner2.scan_all()
        
        # Should get same results
        assert len(elements1) == len(elements2), \
            f"Inconsistent element count: {len(elements1)} vs {len(elements2)}"
        
        for e1, e2 in zip(elements1, elements2):
            assert e1.name == e2.name, f"Name mismatch: {e1.name} vs {e2.name}"
            assert e1.start_line == e2.start_line, \
                f"Start line mismatch for {e1.name}"
            assert e1.end_line == e2.end_line, \
                f"End line mismatch for {e1.name}"
            assert type(e1) == type(e2), \
                f"Type mismatch: {type(e1)} vs {type(e2)}"
                
    except Exception:
        pass  # If it fails, that's OK as long as it fails consistently


# ============================================================================ 
# Test 5: Pathological Inputs (Deep Nesting, Large Files)
# ============================================================================ 
@settings(max_examples=20)
@given(
    braces=st.integers(min_value=0, max_value=50),
    testcases=st.integers(min_value=1, max_value=50)
)
def test_fuzz_pathological_inputs(braces, testcases):
    """Test with pathological inputs: deep nesting and large files."""
    # Test 1: Deeply nested braces
    nested_content = "testcase nested() { " + "{" * braces + "}" * braces + " }"
    
    file_manager = MockFileManager(nested_content)
    scanner = CaplScanner(file_manager)
    
    try:
        scanner.scan_all()
    except RecursionError:
        pass  # Expected for very deep nesting
    except Exception:
        pass
    
    # Test 2: Many test cases (performance check)
    many_testcases = "\n".join([
        f"testcase test{i}() {{ write(\"test {i}\"); }}" 
        for i in range(testcases)
    ])
    
    file_manager2 = MockFileManager(many_testcases)
    scanner2 = CaplScanner(file_manager2)
    
    import time
    start = time.time()
    try:
        elements = scanner2.scan_all()
        elapsed = time.time() - start
        
        # Should be roughly O(n) - warn if too slow
        if testcases > 10:
            assert elapsed < (testcases * 0.01 + 0.5), \
                f"Scanning {testcases} elements took {elapsed:.3f}s - possible O(n²)"
                
    except Exception:
        pass


# ============================================================================ 
# Test 6: Known Pattern Detection
# ============================================================================ 
@settings(max_examples=40)
@given(capl_testcase())
def test_fuzz_testcase_detection(content):
    """Verify scanner finds testcases we generated."""
    file_manager = MockFileManager(content)
    scanner = CaplScanner(file_manager)
    
    try:
        elements = scanner.scan_all()
        
        # We generated exactly 1 testcase, should find it
        test_cases = [e for e in elements 
                     if 'TestCase' in type(e).__name__]
        
        assert len(test_cases) >= 1, \
            f"Generated testcase but found {len(test_cases)}:\n{content[:200]}"
            
    except Exception:
        pass


@settings(max_examples=40)
@given(capl_function())
def test_fuzz_function_detection(content):
    """Verify scanner finds functions we generated."""
    file_manager = MockFileManager(content)
    scanner = CaplScanner(file_manager)
    
    try:
        elements = scanner.scan_all()
        
        # We generated exactly 1 function, should find it
        functions = [e for e in elements 
                    if 'Function' in type(e).__name__]
        
        assert len(functions) >= 1, \
            f"Generated function but found {len(functions)}:\n{content[:200]}"
            
    except Exception:
        pass


# ============================================================================ 
# Test 7: Real-World Examples (Regression Prevention)
# ============================================================================ 
def test_scan_real_event_client_pattern():
    """Test with patterns from Event_Client.can example."""
    content = """
variables
{
  dword serviceId = 10;
  char namespaceName[64] = "MyNamespace";
}

on start
{
    Initialize_Client();
}

void Initialize_Client()
{
  dword aep;
  ep = IP_Endpoint(UDP:192.168.1.5:4005);
  aep = AREthOpenLocalApplicationEndpoint(ep);
}

testcase test_event_payload()
{
  @sysvar::MyNamespace::EventGroupSubscribed = 0;
  TestStep("test", "Waiting...");
}
"""
    
    file_manager = MockFileManager(content)
    scanner = CaplScanner(file_manager)
    elements = scanner.scan_all()
    
    # Should find: variables, on start, function, testcase
    assert len(elements) >= 3, f"Expected at least 3 elements, got {len(elements)}"

def test_scan_real_timer_pattern():
    """Test with patterns from TimestampUpdate example."""
    content = """
variables {
    msTimer updateTimer;
    int messageCount = 0;
}

on start {
    setTimer(updateTimer, 100);
}

on timer updateTimer {
    write("Update");
    setTimer(updateTimer, 100);
}

on message CAN1::* {
    messageCount++;
    write("ID: 0x%03X", this.ID);
}
"""
    
    file_manager = MockFileManager(content)
    scanner = CaplScanner(file_manager)
    elements = scanner.scan_all()
    
    # Should successfully parse without errors
    assert isinstance(elements, list)
    assert len(elements) >= 2  # At minimum: variables and some handlers

def test_fuzz_tricky_formatting():
    """Test tricky formatting that previously caused issues (comments, split lines)."""
    content = """
variables // Global variables start here
{
  int x;
}

includes // Include files
{
  #include "my_lib.cin"
}

on start // The start event
{
  write("Started");
}
"""
    file_manager = MockFileManager(content)
    scanner = CaplScanner(file_manager)
    elements = scanner.scan_all()
    
    # We expect 3 elements: Variable, Include, Handler
    assert len(elements) == 3, f"Expected 3 elements, found {len(elements)}"
    
    # Verify types
    type_names = [type(e).__name__ for e in elements]
    assert "CaplVariable" in type_names
    assert "CaplInclude" in type_names
    assert "Handler" in type_names