import pytest
from pathlib import Path
from envcheck.checker import read_requirements

def test_read_requirements(tmp_path):
    """Test reading requirements from a file."""
    req_file = tmp_path / "requirements.txt"
    req_file.write_text("requests\nnumpy==1.26.0\n# This is a comment\n")

    reqs = read_requirements(str(req_file))
    assert "requests" in reqs
    assert "numpy==1.26.0" in reqs
    assert len(reqs) == 2  # Comments should be ignored

def test_read_requirements_empty_file(tmp_path):
    """Test reading an empty requirements file."""
    req_file = tmp_path / "requirements.txt"
    req_file.write_text("")

    reqs = read_requirements(str(req_file))
    assert reqs == []

def test_read_requirements_with_comments(tmp_path):
    """Test that comments are properly ignored."""
    req_file = tmp_path / "requirements.txt"
    req_file.write_text("requests\n# This is a comment\nnumpy==1.26.0\n")

    reqs = read_requirements(str(req_file))
    assert "requests" in reqs
    assert "numpy==1.26.0" in reqs
    assert len(reqs) == 2
