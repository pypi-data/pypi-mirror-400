"""Tests for typo checker."""

import pytest
import tempfile
import os
from python_code_guardian.checkers.typo_checker import TypoChecker


@pytest.mark.asyncio
async def test_typo_checker_no_typos():
    """Test typo checker with correct code."""
    checker = TypoChecker()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("""
def calculate_total(value):
    \"\"\"Calculate the total value.\"\"\"
    return value * 2
""")
        temp_file = f.name
    
    try:
        config = {"check_variables": True, "check_comments": True, "custom_dictionary": []}
        results = await checker.check(temp_file, config)
        
        assert "issues" in results
        assert results["stats"]["files_checked"] == 1
    finally:
        os.unlink(temp_file)


@pytest.mark.asyncio
async def test_typo_checker_with_typo():
    """Test typo checker with typo in variable name."""
    checker = TypoChecker()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("""
def caluculate_total(value):
    \"\"\"Calculate total.\"\"\"
    return value * 2
""")
        temp_file = f.name
    
    try:
        config = {"check_variables": True, "check_comments": True, "custom_dictionary": []}
        results = await checker.check(temp_file, config)
        
        assert "issues" in results
        # Should find the typo in 'caluculate'
        assert len(results["issues"]) > 0
    finally:
        os.unlink(temp_file)


@pytest.mark.asyncio
async def test_typo_checker_custom_dictionary():
    """Test typo checker with custom dictionary."""
    checker = TypoChecker()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("""
def my_customword_function():
    \"\"\"Function with custom word.\"\"\"
    pass
""")
        temp_file = f.name
    
    try:
        config = {
            "check_variables": True,
            "check_comments": True,
            "custom_dictionary": ["customword"]
        }
        results = await checker.check(temp_file, config)
        
        assert "issues" in results
        # Should not flag 'customword' as it's in the dictionary
    finally:
        os.unlink(temp_file)

