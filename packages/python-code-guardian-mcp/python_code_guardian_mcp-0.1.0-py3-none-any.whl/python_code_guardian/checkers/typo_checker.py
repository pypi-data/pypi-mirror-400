"""Typo detection checker using codespell and custom logic."""

import subprocess
import re
from typing import Any, Dict, List
import ast

from .base_checker import BaseChecker


class TypoChecker(BaseChecker):
    """Checker for typos in comments, docstrings, variables, and strings."""

    def __init__(self):
        """Initialize the typo checker."""
        super().__init__()
        # Common typos and suggestions
        self.common_typos = {
            "caluculate": "calculate",
            "recieve": "receive",
            "seperator": "separator",
            "occured": "occurred",
            "sucessful": "successful",
            "sucessfully": "successfully",
            "connnection": "connection",
            "definately": "definitely",
            "enviroment": "environment",
            "paramter": "parameter",
            "retreive": "retrieve",
            "sucess": "success",
            "teh": "the",
            "lenght": "length",
        }

    async def check(self, path: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check for typos in code.
        
        Args:
            path: File or directory path to check
            config: Configuration including check options
            
        Returns:
            Dictionary containing typo issues
        """
        files = self.get_python_files(path)
        
        if not files:
            return {"issues": [], "stats": {"files_checked": 0, "total_issues": 0}}
        
        all_issues = []
        check_variables = config.get("check_variables", True)
        check_comments = config.get("check_comments", True)
        custom_dictionary = config.get("custom_dictionary", [])
        
        # Add custom words to ignore
        ignored_words = set(custom_dictionary)
        
        for file_path in files:
            issues = await self._check_file(file_path, check_variables, check_comments, ignored_words)
            all_issues.extend(issues)
        
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
        check_variables: bool,
        check_comments: bool,
        ignored_words: set
    ) -> List[Dict[str, Any]]:
        """Check typos in a single file."""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
            
            # Check with codespell first
            try:
                result = subprocess.run(
                    ["codespell", file_path, "--quiet-level=2"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.stdout:
                    for line in result.stdout.strip().split('\n'):
                        if line:
                            # Parse codespell output: filename:line: word ==> suggestion
                            match = re.match(r'([^:]+):(\d+): (.+) ==> (.+)', line)
                            if match:
                                _, line_no, typo, suggestion = match.groups()
                                issue = self.create_issue(
                                    file_path=file_path,
                                    line=int(line_no),
                                    column=0,
                                    severity="info",
                                    code="Typo (Codespell)",
                                    message=f"Possible typo: '{typo}'",
                                    suggestion=f"Did you mean '{suggestion}'?"
                                )
                                issues.append(issue)
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass  # Codespell not available or timed out
            
            # Check variable names if enabled
            if check_variables:
                issues.extend(self._check_variable_names(file_path, content, ignored_words))
            
            # Check comments if enabled
            if check_comments:
                issues.extend(self._check_comments_and_strings(file_path, lines, ignored_words))
        
        except Exception as e:
            issues.append(self.create_issue(
                file_path=file_path,
                line=0,
                column=0,
                severity="error",
                code="Typo (Error)",
                message=f"Failed to check typos: {str(e)}"
            ))
        
        return issues

    def _check_variable_names(self, file_path: str, content: str, ignored_words: set) -> List[Dict[str, Any]]:
        """Check variable and function names for typos."""
        issues = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.Name, ast.FunctionDef, ast.ClassDef)):
                    name = node.name if hasattr(node, 'name') else node.id
                    
                    if name in ignored_words:
                        continue
                    
                    # Check against common typos
                    name_lower = name.lower()
                    for typo, correction in self.common_typos.items():
                        if typo in name_lower:
                            line_no = node.lineno if hasattr(node, 'lineno') else 0
                            suggestion = name.replace(typo, correction)
                            
                            issue = self.create_issue(
                                file_path=file_path,
                                line=line_no,
                                column=node.col_offset if hasattr(node, 'col_offset') else 0,
                                severity="info",
                                code="Typo (Variable)",
                                message=f"Variable/function name '{name}' might contain a typo",
                                suggestion=f"Did you mean '{suggestion}'?"
                            )
                            issues.append(issue)
                            break
        except SyntaxError:
            pass  # Skip files with syntax errors
        
        return issues

    def _check_comments_and_strings(self, file_path: str, lines: List[str], ignored_words: set) -> List[Dict[str, Any]]:
        """Check comments and docstrings for typos."""
        issues = []
        
        for i, line in enumerate(lines, 1):
            # Check comments
            if '#' in line:
                comment = line[line.index('#'):]
                for typo, correction in self.common_typos.items():
                    if re.search(r'\b' + typo + r'\b', comment, re.IGNORECASE):
                        issue = self.create_issue(
                            file_path=file_path,
                            line=i,
                            column=line.index('#'),
                            severity="info",
                            code="Typo (Comment)",
                            message=f"Possible typo in comment: '{typo}'",
                            suggestion=f"Did you mean '{correction}'?"
                        )
                        issues.append(issue)
        
        return issues

    async def fix(self, path: str) -> List[str]:
        """
        Attempt to auto-fix typos.
        
        Args:
            path: File or directory path to fix
            
        Returns:
            List of fixed issue descriptions
        """
        fixed = []
        files = self.get_python_files(path)
        
        for file_path in files:
            try:
                # Use codespell with auto-fix
                result = subprocess.run(
                    ["codespell", "-w", file_path],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    fixed.append(f"Auto-fixed typos in {file_path}")
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass
        
        return fixed

