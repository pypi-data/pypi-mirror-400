import pytest
from pathlib import Path
from capl_tools_lib.file_manager import CaplFileManager

class TestCaplFileManager:
    """Tests for CaplFileManager - focusing on file I/O and comment stripping."""

    @pytest.fixture
    def test_file(self, tmp_path):
        """Create a temporary file for testing."""
        file_path = tmp_path / "sample.can"
        content = [
            "// Header comment\n",
            "variables {\n",
            "  int x = 5; // inline comment\n",
            "}\n",
            "/* block\n",
            "   comment */\n"
        ]
        file_path.write_text("".join(content), encoding="cp1252")
        return file_path

    def test_read_file(self, test_file):
        """Test reading a file."""
        fm = CaplFileManager(test_file)
        assert len(fm.lines) == 6
        assert fm.lines[0] == "// Header comment\n"

    def test_read_file_error(self):
        """Test error handling for non-existent file."""
        with pytest.raises(IOError):
            CaplFileManager(Path("non_existent.can"))

    def test_get_lines(self, test_file):
        """Test retrieving a range of lines."""
        fm = CaplFileManager(test_file)
        lines = fm.get_lines(1, 3)
        assert len(lines) == 2
        assert "variables {" in lines[0]

    def test_get_lines_error(self, test_file):
        """Test error handling for invalid line ranges."""
        fm = CaplFileManager(test_file)
        with pytest.raises(ValueError):
            fm.get_lines(-1, 2)
        with pytest.raises(ValueError):
            fm.get_lines(0, 10)

    def test_write_lines(self, tmp_path, test_file):
        """Test writing lines to a new file."""
        output_path = tmp_path / "output" / "new.can"
        fm = CaplFileManager(test_file)
        
        lines = ["line1\n", "line2\n"]
        fm.write_lines(output_path, lines)
        
        assert output_path.exists()
        assert output_path.read_text(encoding="cp1252") == "line1\nline2\n"

    def test_save_file_new_target(self, tmp_path, test_file):
        """Test saving a file to a new target path (no backup needed)."""
        fm = CaplFileManager(test_file)
        target = tmp_path / "brand_new.can"
        fm.save_file(target, ["content\n"], backup=True)
        assert target.exists()
        assert not target.with_suffix(".can.bak").exists()

    def test_save_file_with_backup(self, test_file):
        """Test saving a file with backup creation."""
        fm = CaplFileManager(test_file)
        new_lines = ["new content\n"]
        fm.save_file(test_file, new_lines, backup=True)
        
        bak_file = test_file.with_suffix(".can.bak")
        assert bak_file.exists()
        assert "variables {" in bak_file.read_text(encoding="cp1252")
        assert test_file.read_text(encoding="cp1252") == "new content\n"

    def test_strip_comments(self, test_file):
        """Test stripping // comments."""
        fm = CaplFileManager(test_file)
        stripped = fm.strip_comments()
        
        assert "variables {" in stripped
        assert "int x = 5;" in stripped[1]
        assert "// Header comment" not in "".join(stripped)
        assert "// inline comment" not in "".join(stripped)
