"""Base class for all code checkers."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
import os


class BaseChecker(ABC):
    """Base class for code quality checkers."""

    def __init__(self):
        """Initialize the base checker."""
        self.name = self.__class__.__name__

    @abstractmethod
    async def check(self, path: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the check on the specified path.
        
        Args:
            path: File or directory path to check
            config: Configuration for this checker
            
        Returns:
            Dictionary containing check results with 'issues' list
        """
        pass

    def is_python_file(self, file_path: str) -> bool:
        """Check if a file is a Python file."""
        return file_path.endswith('.py')

    def get_python_files(self, path: str) -> List[str]:
        """
        Get all Python files in the specified path.
        
        Args:
            path: File or directory path
            
        Returns:
            List of Python file paths
        """
        if os.path.isfile(path):
            return [path] if self.is_python_file(path) else []
        
        python_files = []
        for root, _, files in os.walk(path):
            # Skip common directories
            if any(skip in root for skip in ['.git', '__pycache__', 'venv', '.venv', 'node_modules']):
                continue
                
            for file in files:
                if self.is_python_file(file):
                    python_files.append(os.path.join(root, file))
        
        return python_files

    def create_issue(
        self,
        file_path: str,
        line: int,
        column: int,
        severity: str,
        code: str,
        message: str,
        suggestion: str = None
    ) -> Dict[str, Any]:
        """
        Create a standardized issue dictionary.
        
        Args:
            file_path: Path to the file with the issue
            line: Line number
            column: Column number
            severity: One of 'error', 'warning', 'info'
            code: Issue code or category
            message: Issue description
            suggestion: Optional suggestion for fixing
            
        Returns:
            Issue dictionary
        """
        issue = {
            "file": file_path,
            "line": line,
            "column": column,
            "severity": severity,
            "code": code,
            "message": message,
        }
        
        if suggestion:
            issue["suggestion"] = suggestion
        
        return issue

