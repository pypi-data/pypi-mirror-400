"""Code structure and organization checker."""

import os
import ast
from typing import Any, Dict, List
import re

from .base_checker import BaseChecker


class StructureChecker(BaseChecker):
    """Checker for code structure, organization, and naming conventions."""

    async def check(self, path: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check code structure and organization.
        
        Args:
            path: File or directory path to check
            config: Configuration including naming conventions, docstring requirements
            
        Returns:
            Dictionary containing structure issues
        """
        files = self.get_python_files(path)
        
        if not files:
            return {"issues": [], "stats": {"files_checked": 0, "total_issues": 0}}
        
        all_issues = []
        require_docstrings = config.get("require_docstrings", True)
        naming_convention = config.get("naming_convention", "snake_case")
        
        for file_path in files:
            issues = await self._check_file(file_path, require_docstrings, naming_convention)
            all_issues.extend(issues)
        
        # Check directory structure if checking a directory
        if os.path.isdir(path):
            all_issues.extend(self._check_directory_structure(path))
        
        return {
            "issues": all_issues,
            "stats": {
                "files_checked": len(files),
                "total_issues": len(all_issues)
            }
        }

    async def _check_file(
        self,
        file_path: str,
        require_docstrings: bool,
        naming_convention: str
    ) -> List[Dict[str, Any]]:
        """Check structure of a single file."""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check file naming convention
            filename = os.path.basename(file_path)
            if not self._check_naming_convention(filename[:-3], naming_convention):  # Remove .py
                issue = self.create_issue(
                    file_path=file_path,
                    line=0,
                    column=0,
                    severity="info",
                    code="NamingConvention (File)",
                    message=f"File name '{filename}' doesn't follow {naming_convention} convention",
                    suggestion=f"Use {naming_convention} for file names"
                )
                issues.append(issue)
            
            # Parse AST
            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                issue = self.create_issue(
                    file_path=file_path,
                    line=e.lineno if hasattr(e, 'lineno') else 0,
                    column=0,
                    severity="error",
                    code="SyntaxError",
                    message=f"Syntax error: {str(e)}",
                    suggestion="Fix syntax errors before running other checks"
                )
                issues.append(issue)
                return issues
            
            # Check module docstring
            if require_docstrings:
                if not ast.get_docstring(tree):
                    issue = self.create_issue(
                        file_path=file_path,
                        line=1,
                        column=0,
                        severity="warning",
                        code="MissingDocstring (Module)",
                        message="Module is missing a docstring",
                        suggestion="Add a module-level docstring describing the file's purpose"
                    )
                    issues.append(issue)
            
            # Check functions and classes
            for node in ast.walk(tree):
                # Check function/method docstrings
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if require_docstrings and not ast.get_docstring(node):
                        # Skip private methods
                        if not node.name.startswith('_') or node.name.startswith('__'):
                            issue = self.create_issue(
                                file_path=file_path,
                                line=node.lineno,
                                column=node.col_offset,
                                severity="warning",
                                code="MissingDocstring (Function)",
                                message=f"Function '{node.name}' is missing a docstring",
                                suggestion="Add a docstring describing the function's purpose, args, and return value"
                            )
                            issues.append(issue)
                    
                    # Check function naming
                    if not self._check_naming_convention(node.name, naming_convention):
                        issue = self.create_issue(
                            file_path=file_path,
                            line=node.lineno,
                            column=node.col_offset,
                            severity="info",
                            code="NamingConvention (Function)",
                            message=f"Function name '{node.name}' doesn't follow {naming_convention} convention",
                            suggestion=f"Use {naming_convention} for function names"
                        )
                        issues.append(issue)
                
                # Check class docstrings
                elif isinstance(node, ast.ClassDef):
                    if require_docstrings and not ast.get_docstring(node):
                        issue = self.create_issue(
                            file_path=file_path,
                            line=node.lineno,
                            column=node.col_offset,
                            severity="warning",
                            code="MissingDocstring (Class)",
                            message=f"Class '{node.name}' is missing a docstring",
                            suggestion="Add a docstring describing the class's purpose"
                        )
                        issues.append(issue)
                    
                    # Check class naming (should be PascalCase)
                    if not self._is_pascal_case(node.name):
                        issue = self.create_issue(
                            file_path=file_path,
                            line=node.lineno,
                            column=node.col_offset,
                            severity="info",
                            code="NamingConvention (Class)",
                            message=f"Class name '{node.name}' should use PascalCase",
                            suggestion="Use PascalCase for class names (e.g., MyClassName)"
                        )
                        issues.append(issue)
        
        except Exception as e:
            issues.append(self.create_issue(
                file_path=file_path,
                line=0,
                column=0,
                severity="error",
                code="Structure (Error)",
                message=f"Failed to check structure: {str(e)}"
            ))
        
        return issues

    def _check_naming_convention(self, name: str, convention: str) -> bool:
        """Check if name follows the specified convention."""
        if convention == "snake_case":
            return self._is_snake_case(name)
        elif convention == "camelCase":
            return self._is_camel_case(name)
        elif convention == "PascalCase":
            return self._is_pascal_case(name)
        return True

    def _is_snake_case(self, name: str) -> bool:
        """Check if name is snake_case."""
        # Allow dunder methods
        if name.startswith('__') and name.endswith('__'):
            return True
        # Allow private methods
        if name.startswith('_'):
            name = name[1:]
        return bool(re.match(r'^[a-z0-9_]+$', name))

    def _is_camel_case(self, name: str) -> bool:
        """Check if name is camelCase."""
        return bool(re.match(r'^[a-z][a-zA-Z0-9]*$', name))

    def _is_pascal_case(self, name: str) -> bool:
        """Check if name is PascalCase."""
        return bool(re.match(r'^[A-Z][a-zA-Z0-9]*$', name))

    def _check_directory_structure(self, path: str) -> List[Dict[str, Any]]:
        """Check directory structure for best practices."""
        issues = []
        
        # Check for __init__.py files in subdirectories
        for root, dirs, files in os.walk(path):
            # Skip common directories
            if any(skip in root for skip in ['.git', '__pycache__', 'venv', '.venv', 'node_modules']):
                continue
            
            # Check if subdirectories have __init__.py
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                init_file = os.path.join(dir_path, '__init__.py')
                
                # Check if directory contains Python files
                has_python_files = any(
                    f.endswith('.py') for f in os.listdir(dir_path)
                    if os.path.isfile(os.path.join(dir_path, f))
                )
                
                if has_python_files and not os.path.exists(init_file):
                    issue = self.create_issue(
                        file_path=dir_path,
                        line=0,
                        column=0,
                        severity="info",
                        code="Structure (Missing __init__.py)",
                        message=f"Directory '{dir_name}' contains Python files but no __init__.py",
                        suggestion="Add __init__.py to make it a proper Python package"
                    )
                    issues.append(issue)
        
        return issues

