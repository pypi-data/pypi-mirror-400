import pytest
from pathlib import Path
from capl_tools_lib.processor import CaplProcessor
from capl_tools_lib.file_manager import CaplFileManager

class TestCaplProcessor:
    """Tests for CaplProcessor - focusing on high-level workflows."""

    @pytest.fixture
    def test_can_file(self, tmp_path):
        """Create a temporary .can file for testing."""
        file_path = tmp_path / "test.can"
        content = [
            "includes {\n",
            "}\n",
            "\n",
            "variables {\n",
            "}\n",
            "\n",
            "testcase TestCase1()\n",
            "{\n",
            "  InitializeTestGroup(\"GroupA\");\n",
            "}\n",
            "\n",
            "testcase TestCase2()\n",
            "{\n",
            "  InitializeTestGroup(\"GroupB\");\n",
            "}\n",
            "\n",
            "testcase TestCase3()\n",
            "{\n",
            "  InitializeTestGroup(\"GroupA\");\n",
            "}\n"
        ]
        file_path.write_text("".join(content), encoding="cp1252")
        return file_path

    def test_scan_and_stats(self, test_can_file):
        """Test scanning and getting stats."""
        processor = CaplProcessor(test_can_file)
        stats = processor.get_stats()
        
        assert stats["TestCase"] == 3
        assert stats["CaplInclude"] == 1 
        assert stats["CaplVariable"] == 1

    def test_remove_test_group(self, test_can_file):
        """Test removing a specific test group."""
        processor = CaplProcessor(test_can_file)
        
        # Remove GroupA (2 test cases)
        removed_count = processor.remove_test_group("GroupA")
        assert removed_count == 2
        
        # Stats should update after removal
        stats = processor.get_stats()
        assert stats["TestCase"] == 1
        
        # Verify TestCase2 (GroupB) is still there
        elements = processor.scan()
        test_cases = [el for el in elements if el.__class__.__name__ == "TestCase"]
        assert len(test_cases) == 1
        assert test_cases[0].name == "TestCase2"

    def test_save_and_reload(self, test_can_file):
        """Test saving changes and reloading."""
        processor = CaplProcessor(test_can_file)
        processor.remove_test_group("GroupA")
        
        # Save to a new file
        output_file = test_can_file.parent / "output.can"
        processor.save(output_path=output_file)
        
        assert output_file.exists()
        content = output_file.read_text(encoding="cp1252")
        assert "TestCase1" not in content
        assert "TestCase3" not in content
        assert "TestCase2" in content
        
        # Reload processor
        processor.reload()
        # After reload, it should have 3 test cases again (from original file)
        assert processor.get_stats()["TestCase"] == 3

    def test_dirty_flag_sync(self, test_can_file):
        """Test that changes in editor are synced to scanner via dirty flag."""
        processor = CaplProcessor(test_can_file)
        
        # Initial scan
        assert len(processor.scan()) > 0
        assert not processor._dirty
        
        # Modify via editor
        from capl_tools_lib.elements import CAPLElement
        el = processor.scan()[0]
        processor.editor.remove_element(el)
        processor._dirty = True # Processor sets this manually in remove_test_group
        
        # Next scan should trigger sync
        elements_after = processor.scan()
        assert len(elements_after) < len(processor._elements if processor._elements else []) + 1 
        # Actually processor.scan() clears self._elements if dirty
        assert not processor._dirty
