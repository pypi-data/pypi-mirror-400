import pytest
from capl_tools_lib.editor import CaplEditor
from capl_tools_lib.elements import CAPLElement

class TestCaplEditor:
    """Tests for CaplEditor - focused on in-memory line manipulation."""

    @pytest.fixture
    def initial_lines(self):
        """Provide a standard set of lines for testing."""
        return [
            "includes\n",
            "{\n",
            "}\n",
            "\n",
            "variables\n",
            "{\n",
            "  int gVar = 0;\n",
            "}\n",
            "\n",
            "testcase MyTestCase()\n",
            "{\n",
            "  write(\"Hello\");\n",
            "}\n"
        ]

    @pytest.fixture
    def editor(self, initial_lines):
        """Create a CaplEditor instance with initial lines."""
        return CaplEditor(lines=initial_lines)

    def test_init_with_lines(self, initial_lines):
        """Verify editor initializes correctly with a list of lines."""
        editor = CaplEditor(lines=initial_lines)
        assert editor.get_lines() == initial_lines

    def test_init_error(self):
        """Verify editor raises ValueError if no source is provided."""
        with pytest.raises(ValueError, match="Either file_mngr or lines must be provided"):
            CaplEditor()

    def test_delete_lines(self, editor):
        """Test deleting a range of lines."""
        # Delete MyTestCase (lines 9 to 12 inclusive, so 9:13)
        editor.delete_lines(9, 13)
        lines = editor.get_lines()
        assert len(lines) == 9
        assert "testcase MyTestCase()" not in lines[-1]

    def test_delete_lines_invalid_range(self, editor):
        """Test that invalid ranges raise ValueError."""
        with pytest.raises(ValueError):
            editor.delete_lines(-1, 5)
        with pytest.raises(ValueError):
            editor.delete_lines(5, 2)
        with pytest.raises(ValueError):
            editor.delete_lines(0, 100)

    def test_insert_lines(self, editor):
        """Test inserting lines at a specific position."""
        new_lines = ["// New Comment\n", "int gNewVar = 1;\n"]
        # Insert after variables block (position 8)
        editor.insert_lines(8, new_lines)
        lines = editor.get_lines()
        assert lines[8] == "// New Comment\n"
        assert lines[9] == "int gNewVar = 1;\n"
        assert len(lines) == 13 + 2

    def test_replace_lines(self, editor):
        """Test replacing a range of lines."""
        replacement = ["testcase UpdatedCase()\n", "{\n", "}\n"]
        # Replace MyTestCase (9 to 12)
        editor.replace_lines(9, 13, replacement)
        lines = editor.get_lines()
        assert "testcase UpdatedCase()\n" in lines
        assert "testcase MyTestCase()\n" not in lines

    def test_remove_element(self, editor):
        """Test removing a CAPLElement."""
        # Mock a CAPLElement
        element = CAPLElement(name="MyTestCase", start_line=9, end_line=12)
        editor.remove_element(element)
        lines = editor.get_lines()
        assert len(lines) == 9
        assert "testcase MyTestCase()\n" not in lines

    def test_insert_element(self, editor):
        """Test inserting a new element (lines) at a position."""
        element_lines = ["void NewFunc()\n", "{\n", "}\n"]
        editor.insert_element(0, element_lines)
        assert editor.get_lines()[:3] == element_lines

    def test_reset(self, initial_lines):
        """Test resetting the editor to the original state."""
        from unittest.mock import MagicMock
        mock_fm = MagicMock()
        mock_fm.lines = initial_lines
        
        editor = CaplEditor(file_mngr=mock_fm)
        editor.delete_lines(0, 5)
        assert len(editor.get_lines()) < len(initial_lines)
        
        editor.reset()
        assert editor.get_lines() == initial_lines

    def test_init_with_file_mngr(self, initial_lines):
        """Verify editor initializes correctly with a file manager."""
        from unittest.mock import MagicMock
        mock_fm = MagicMock()
        mock_fm.lines = initial_lines
        
        editor = CaplEditor(file_mngr=mock_fm)
        assert editor.get_lines() == initial_lines
        assert editor.file_mngr == mock_fm

    def test_insert_lines_invalid_position(self, editor):
        """Test that invalid insertion positions raise ValueError."""
        with pytest.raises(ValueError):
            editor.insert_lines(-1, ["// error\n"])
        with pytest.raises(ValueError):
            editor.insert_lines(100, ["// error\n"])

    def test_get_modified_lines_internal(self, editor, initial_lines):
        """Test the internal _get_modified_lines method."""
        assert editor._get_modified_lines() == initial_lines
