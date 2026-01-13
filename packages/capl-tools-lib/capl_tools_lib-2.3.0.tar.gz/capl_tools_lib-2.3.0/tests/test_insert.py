import pytest
from pathlib import Path
from capl_tools_lib.processor import CaplProcessor

def test_insert_with_string(tmp_path):
    """Test inserting code directly from string"""
    # Create a temporary CAPL file
    test_file = tmp_path / "test.can"
    test_file.write_text("""
void testFunction() {
    write("test");
}
""")
    
    # Code to insert
    new_code = """testcase TC_New() {
    write("New test");
}"""
    
    # Insert using string
    processor = CaplProcessor(test_file)
    result = processor.insert(
        location="after:testFunction",
        element_type="TestCase",
        code_string=new_code
    )
    
    assert result is True # Returns success status
    
    # Verify insertion
    # Note: Processor keeps changes in memory editor until save() is called if we want to read file back?
    # Or get_lines() from editor.
    # The processor.insert docs say it inserts into editor.
    # To verify content, we can check processor.editor.get_lines() or save and read.
    # Let's check lines from editor for speed, or save for robustness.
    # The original test checked file content so let's save.
    processor.save()
    
    content = test_file.read_text()
    assert "TC_New" in content
    assert "New test" in content


def test_insert_with_file(tmp_path):
    """Test inserting code from file (existing behavior)"""
    test_file = tmp_path / "test.can"
    snippet_file = tmp_path / "snippet.can"
    
    test_file.write_text("void testFunction() { }")
    snippet_file.write_text("testcase TC_FromFile() { }")
    
    processor = CaplProcessor(test_file)
    result = processor.insert(
        location="after:testFunction",
        element_type="TestCase",
        source=snippet_file
    )
    
    assert result is True
    processor.save()
    
    assert "TC_FromFile" in test_file.read_text()


def test_insert_requires_source_or_code(tmp_path):
    """Test that insert raises error when neither source nor code provided"""
    test_file = tmp_path / "dummy.can"
    test_file.touch()
    processor = CaplProcessor(test_file)
    
    with pytest.raises(ValueError, match="Must provide either"):
        processor.insert(
            location="after:something",
            element_type="TestCase"
        )


def test_insert_rejects_both_source_and_code(tmp_path):
    """Test that insert raises error when both source and code provided"""
    test_file = tmp_path / "dummy.can"
    test_file.touch()
    processor = CaplProcessor(test_file)
    
    with pytest.raises(ValueError, match="Cannot provide both"):
        processor.insert(
            location="after:something",
            element_type="TestCase",
            source=Path("file.can"),
            code_string="code here"
        )
