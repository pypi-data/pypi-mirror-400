"""Pylint-based linting checker."""

import subprocess
import json
from typing import Any, Dict, List

from .base_checker import BaseChecker


class LintChecker(BaseChecker):
    """Checker for linting issues using Pylint."""

    async def check(self, path: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run Pylint checks on the specified path.
        
        Args:
            path: File or directory path to check
            config: Configuration for Pylint
            
        Returns:
            Dictionary containing lint issues
        """
        files = self.get_python_files(path)
        
        if not files:
            return {"issues": [], "stats": {"files_checked": 0, "total_issues": 0}}
        
        all_issues = []
        
        for file_path in files:
            issues = await self._check_file(file_path, config)
            all_issues.extend(issues)
        
        return {
            "issues": all_issues,
            "stats": {
                "files_checked": len(files),
                "total_issues": len(all_issues)
            }
        }

    async def _check_file(self, file_path: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Run Pylint on a single file."""
        issues = []
        
        try:
            # Prepare Pylint arguments
            args = [file_path]
            
            # Add configuration options
            if config.get("max_line_length"):
                args.append(f"--max-line-length={config['max_line_length']}")
            
            if config.get("disable"):
                disabled_checks = ",".join(config["disable"])
                args.append(f"--disable={disabled_checks}")
            
            # Add output format
            args.extend(["--output-format=json", "--reports=n"])
            
            # Run Pylint
            result = subprocess.run(
                ["pylint"] + args,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse JSON output
            if result.stdout:
                try:
                    pylint_results = json.loads(result.stdout)
                    
                    for item in pylint_results:
                        severity = self._map_severity(item.get("type", "convention"))
                        
                        issue = self.create_issue(
                            file_path=file_path,
                            line=item.get("line", 0),
                            column=item.get("column", 0),
                            severity=severity,
                            code=f"Pylint ({item.get('message-id', 'unknown')})",
                            message=item.get("message", ""),
                            suggestion=self._get_suggestion(item)
                        )
                        issues.append(issue)
                except json.JSONDecodeError:
                    pass  # No valid JSON output
        
        except subprocess.TimeoutExpired:
            issues.append(self.create_issue(
                file_path=file_path,
                line=0,
                column=0,
                severity="error",
                code="Pylint (Timeout)",
                message="Pylint check timed out"
            ))
        except FileNotFoundError:
            issues.append(self.create_issue(
                file_path=file_path,
                line=0,
                column=0,
                severity="error",
                code="Pylint (Not Found)",
                message="Pylint is not installed. Run: pip install pylint"
            ))
        except Exception as e:
            issues.append(self.create_issue(
                file_path=file_path,
                line=0,
                column=0,
                severity="error",
                code="Pylint (Error)",
                message=f"Failed to run Pylint: {str(e)}"
            ))
        
        return issues

    def _map_severity(self, pylint_type: str) -> str:
        """Map Pylint message types to severity levels."""
        mapping = {
            "error": "error",
            "fatal": "error",
            "warning": "warning",
            "convention": "info",
            "refactor": "info",
            "information": "info"
        }
        return mapping.get(pylint_type.lower(), "info")

    def _get_suggestion(self, item: Dict[str, Any]) -> str:
        """Generate suggestion based on Pylint message."""
        message_id = item.get("message-id", "")
        suggestions = {
            "C0301": "Consider breaking long lines or using implicit line continuation",
            "C0103": "Use snake_case for variable names",
            "C0111": "Add a docstring describing the module, function, or class",
            "W0611": "Remove unused imports",
            "W0612": "Remove unused variables or prefix with underscore",
        }
        return suggestions.get(message_id, "")

    async def fix(self, path: str) -> List[str]:
        """
        Attempt to auto-fix lint issues.
        
        Args:
            path: File or directory path to fix
            
        Returns:
            List of fixed issue descriptions
        """
        fixed = []
        files = self.get_python_files(path)
        
        for file_path in files:
            try:
                # Try using black for formatting
                result = subprocess.run(
                    ["black", "--quiet", file_path],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    fixed.append(f"Auto-formatted {file_path} with black")
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass  # Black not available or failed
        
        return fixed

