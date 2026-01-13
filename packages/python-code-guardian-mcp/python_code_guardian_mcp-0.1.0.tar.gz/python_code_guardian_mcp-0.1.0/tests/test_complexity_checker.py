"""Tests for complexity checker."""

import pytest
import tempfile
import os
from python_code_guardian.checkers.complexity_checker import ComplexityChecker


@pytest.mark.asyncio
async def test_complexity_checker_simple_function():
    """Test complexity checker with simple function."""
    checker = ComplexityChecker()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("""
def simple_function(x):
    \"\"\"Simple function with low complexity.\"\"\"
    return x + 1
""")
        temp_file = f.name
    
    try:
        config = {"max_complexity": 10, "max_function_length": 50}
        results = await checker.check(temp_file, config)
        
        assert "issues" in results
        assert results["stats"]["files_checked"] == 1
        # Should have no issues for simple function
        assert len(results["issues"]) == 0
    finally:
        os.unlink(temp_file)


@pytest.mark.asyncio
async def test_complexity_checker_complex_function():
    """Test complexity checker with complex function."""
    checker = ComplexityChecker()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("""
def complex_function(x, y, z):
    \"\"\"Complex function with high complexity.\"\"\"
    if x > 0:
        if y > 0:
            if z > 0:
                return x + y + z
            else:
                return x + y
        else:
            if z > 0:
                return x + z
            else:
                return x
    else:
        if y > 0:
            if z > 0:
                return y + z
            else:
                return y
        else:
            return z
""")
        temp_file = f.name
    
    try:
        config = {"max_complexity": 5, "max_function_length": 50}
        results = await checker.check(temp_file, config)
        
        assert "issues" in results
        # Should find complexity issues
        assert len(results["issues"]) > 0
    finally:
        os.unlink(temp_file)

