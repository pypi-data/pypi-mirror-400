# tests/test_analyze_source.py
"""Tests for source reference handler."""
import json
import tempfile
from pathlib import Path

import pytest

from cdd_tooling.analyze.source import (
    SOURCE_EXTENSIONS,
    analyze_source,
    compare_source_analyses,
    compute_hash,
    count_lines,
    get_file_type,
    is_source_file,
)


class TestIsSourceFile:
    def test_python_files(self):
        assert is_source_file(Path("test.py"))
        assert is_source_file(Path("test.pyi"))
        
    def test_javascript_files(self):
        assert is_source_file(Path("test.js"))
        assert is_source_file(Path("test.jsx"))
        assert is_source_file(Path("test.ts"))
        assert is_source_file(Path("test.tsx"))
        
    def test_supercollider_files(self):
        assert is_source_file(Path("test.scd"))
        assert is_source_file(Path("test.sc"))
        
    def test_config_files(self):
        assert is_source_file(Path("test.yaml"))
        assert is_source_file(Path("test.yml"))
        assert is_source_file(Path("test.json"))
        assert is_source_file(Path("test.toml"))
        
    def test_unsupported_files(self):
        assert not is_source_file(Path("test.pdf"))
        assert not is_source_file(Path("test.html"))
        assert not is_source_file(Path("test.png"))
        assert not is_source_file(Path("test.unknown"))


class TestGetFileType:
    def test_python(self):
        assert get_file_type(Path("test.py")) == "python"
        
    def test_supercollider(self):
        assert get_file_type(Path("test.scd")) == "supercollider"
        
    def test_unknown(self):
        assert get_file_type(Path("test.unknown")) is None


class TestAnalyzeSource:
    def test_analyze_python_file(self, tmp_path):
        # Create a sample Python file
        source_file = tmp_path / "sample.py"
        source_file.write_text("def hello():\n    print('Hello')\n")
        
        output_dir = tmp_path / "analysis"
        result = analyze_source(source_file, output_dir)
        
        # Check result structure
        assert result["type"] == "source_reference"
        assert result["file_type"] == "python"
        assert result["source_name"] == "sample.py"
        assert result["line_count"] == 2
        assert "hash" in result
        
        # Check files were created
        assert (output_dir / "source.py").exists()
        assert (output_dir / "structure.json").exists()
        assert (output_dir / "PATTERNS.md").exists()
        assert (output_dir / "elements.md").exists()
        
        # Check structure.json content
        structure = json.loads((output_dir / "structure.json").read_text())
        assert structure["type"] == "source_reference"
        assert structure["file_type"] == "python"
        
    def test_analyze_supercollider_file(self, tmp_path):
        source_file = tmp_path / "synth.scd"
        source_file.write_text("SynthDef(\\test, { Out.ar(0, SinOsc.ar) });")
        
        output_dir = tmp_path / "analysis"
        result = analyze_source(source_file, output_dir)
        
        assert result["type"] == "source_reference"
        assert result["file_type"] == "supercollider"
        assert (output_dir / "source.scd").exists()
        
        # Check PATTERNS.md has SC-specific section
        patterns = (output_dir / "PATTERNS.md").read_text()
        assert "SuperCollider-Specific" in patterns
        
    def test_analyze_nonexistent_file(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            analyze_source(tmp_path / "nonexistent.py", tmp_path / "out")
            
    def test_analyze_unsupported_type(self, tmp_path):
        source_file = tmp_path / "test.pdf"
        source_file.write_bytes(b"%PDF-1.4")
        
        with pytest.raises(ValueError, match="Unsupported source type"):
            analyze_source(source_file, tmp_path / "out")


class TestCompareSourceAnalyses:
    def test_identical_files(self):
        original = {
            "type": "source_reference",
            "hash": "abc123",
            "file_type": "python",
            "line_count": 10,
        }
        generated = {
            "type": "source_reference",
            "hash": "abc123",
            "file_type": "python",
            "line_count": 10,
        }
        
        result = compare_source_analyses(original, generated)
        assert result["match"] is True
        assert "identical" in result["summary"]
        
    def test_different_files(self):
        original = {
            "type": "source_reference",
            "hash": "abc123",
            "file_type": "python",
            "line_count": 10,
        }
        generated = {
            "type": "source_reference",
            "hash": "def456",
            "file_type": "python",
            "line_count": 15,
        }
        
        result = compare_source_analyses(original, generated)
        assert result["match"] is False
        assert "+5 lines" in result["summary"]
        
    def test_different_types(self):
        original = {
            "type": "source_reference",
            "hash": "abc123",
            "file_type": "python",
            "line_count": 10,
        }
        generated = {
            "type": "source_reference",
            "hash": "abc123",
            "file_type": "javascript",
            "line_count": 10,
        }
        
        result = compare_source_analyses(original, generated)
        assert result["file_type_match"] is False


class TestUtilityFunctions:
    def test_compute_hash(self, tmp_path):
        file1 = tmp_path / "a.txt"
        file2 = tmp_path / "b.txt"
        file1.write_text("hello")
        file2.write_text("hello")
        
        # Same content should have same hash
        assert compute_hash(file1) == compute_hash(file2)
        
        # Different content should have different hash
        file2.write_text("world")
        assert compute_hash(file1) != compute_hash(file2)
        
    def test_count_lines(self, tmp_path):
        file = tmp_path / "test.txt"
        file.write_text("line1\nline2\nline3\n")
        assert count_lines(file) == 3
        
    def test_count_lines_empty(self, tmp_path):
        file = tmp_path / "empty.txt"
        file.write_text("")
        assert count_lines(file) == 0
