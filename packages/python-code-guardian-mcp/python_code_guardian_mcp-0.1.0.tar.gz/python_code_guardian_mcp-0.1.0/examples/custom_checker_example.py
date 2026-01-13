"""Example custom checker for Python Code Guardian."""

from python_code_guardian.checkers import BaseChecker
from typing import Any, Dict, List


class TODOChecker(BaseChecker):
    """Custom checker that flags TODO comments."""
    
    async def check(self, path: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check for TODO comments in code.
        
        Args:
            path: File or directory to check
            config: Configuration dictionary
            
        Returns:
            Dictionary with issues found
        """
        files = self.get_python_files(path)
        all_issues = []
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line_no, line in enumerate(f, 1):
                        if 'TODO' in line or 'FIXME' in line:
                            issue = self.create_issue(
                                file_path=file_path,
                                line=line_no,
                                column=0,
                                severity="info",
                                code="TODO-CHECK",
                                message="TODO/FIXME comment found",
                                suggestion="Consider creating a ticket or issue"
                            )
                            all_issues.append(issue)
            except Exception:
                pass  # Skip files that can't be read
        
        return {
            "issues": all_issues,
            "stats": {
                "files_checked": len(files),
                "total_issues": len(all_issues)
            }
        }


class PrintStatementChecker(BaseChecker):
    """Custom checker that flags print() statements (should use logging)."""
    
    async def check(self, path: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check for print statements that should use logging."""
        import ast
        
        files = self.get_python_files(path)
        all_issues = []
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Name) and node.func.id == 'print':
                            issue = self.create_issue(
                                file_path=file_path,
                                line=node.lineno,
                                column=node.col_offset,
                                severity="warning",
                                code="PRINT-STATEMENT",
                                message="Use logging instead of print()",
                                suggestion="Replace with: logging.info(...) or logging.debug(...)"
                            )
                            all_issues.append(issue)
            except (SyntaxError, Exception):
                pass  # Skip files with syntax errors
        
        return {
            "issues": all_issues,
            "stats": {
                "files_checked": len(files),
                "total_issues": len(all_issues)
            }
        }


# To use these custom checkers, add them to your .code-guardian.yaml:
# custom_checkers:
#   - path: ./custom_checker_example.py
#     class: TODOChecker
#   - path: ./custom_checker_example.py
#     class: PrintStatementChecker

