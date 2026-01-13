"""Python Code Guardian MCP Server.

A comprehensive MCP server for Python code quality checks including:
- Linting with Pylint
- Code complexity and modularity checks
- Typo detection
- Code structure validation
- Test coverage analysis
"""

__version__ = "0.1.0"
__author__ = "Priyanshi Jajoo"
__license__ = "MIT"

from .server import create_server

__all__ = ["create_server", "__version__"]

