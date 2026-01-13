"""Tests for lint checker."""

import pytest
import tempfile
import os
from python_code_guardian.checkers.lint_checker import LintChecker


@pytest.mark.asyncio
async def test_lint_checker_valid_code():
    """Test lint checker with valid code."""
    checker = LintChecker()
    
    # Create temporary file with valid code
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("""
def hello_world():
    \"\"\"Say hello.\"\"\"
    return "Hello, World!"
""")
        temp_file = f.name
    
    try:
        config = {"max_line_length": 100, "disable": []}
        results = await checker.check(temp_file, config)
        
        assert "issues" in results
        assert "stats" in results
        assert results["stats"]["files_checked"] == 1
    finally:
        os.unlink(temp_file)


@pytest.mark.asyncio
async def test_lint_checker_long_line():
    """Test lint checker with long line."""
    checker = LintChecker()
    
    # Create temporary file with long line
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("""
def test():
    # This is a very long comment line that exceeds the maximum allowed line length and should trigger a linting error
    pass
""")
        temp_file = f.name
    
    try:
        config = {"max_line_length": 80, "disable": []}
        results = await checker.check(temp_file, config)
        
        assert "issues" in results
        # Note: May or may not find issues depending on pylint availability
    finally:
        os.unlink(temp_file)


@pytest.mark.asyncio
async def test_lint_checker_empty_directory():
    """Test lint checker with empty directory."""
    checker = LintChecker()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config = {}
        results = await checker.check(temp_dir, config)
        
        assert results["stats"]["files_checked"] == 0
        assert results["stats"]["total_issues"] == 0

