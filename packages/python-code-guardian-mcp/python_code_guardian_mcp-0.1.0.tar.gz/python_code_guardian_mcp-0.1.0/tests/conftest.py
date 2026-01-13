"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture
def sample_python_code():
    """Sample Python code for testing."""
    return """
def hello_world():
    \"\"\"Say hello to the world.\"\"\"
    message = "Hello, World!"
    return message


class Calculator:
    \"\"\"Simple calculator class.\"\"\"
    
    def add(self, a, b):
        \"\"\"Add two numbers.\"\"\"
        return a + b
    
    def subtract(self, a, b):
        \"\"\"Subtract two numbers.\"\"\"
        return a - b
"""


@pytest.fixture
def bad_python_code():
    """Python code with issues for testing."""
    return """
def caluculate_total(x,y,z):  # Typo in function name, missing spaces
    if x>0:  # Missing spaces around operator
        if y>0:
            if z>0:
                return x+y+z
            else:
                return x+y
        else:
            return x
    return 0
"""

