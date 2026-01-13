"""Complexity and modularity checker using Radon."""

from typing import Any, Dict, List
from radon.complexity import cc_visit
from radon.metrics import mi_visit, mi_rank

from .base_checker import BaseChecker


class ComplexityChecker(BaseChecker):
    """Checker for code complexity and modularity."""

    async def check(self, path: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check code complexity and modularity.
        
        Args:
            path: File or directory path to check
            config: Configuration including max_complexity, max_function_length
            
        Returns:
            Dictionary containing complexity issues
        """
        files = self.get_python_files(path)
        
        if not files:
            return {"issues": [], "stats": {"files_checked": 0, "total_issues": 0}}
        
        all_issues = []
        max_complexity = config.get("max_complexity", 10)
        max_function_length = config.get("max_function_length", 50)
        
        for file_path in files:
            issues = await self._check_file(file_path, max_complexity, max_function_length)
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
        max_complexity: int,
        max_function_length: int
    ) -> List[Dict[str, Any]]:
        """Check complexity of a single file."""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Check cyclomatic complexity
            try:
                complexity_results = cc_visit(code)
                
                for item in complexity_results:
                    if item.complexity > max_complexity:
                        issue = self.create_issue(
                            file_path=file_path,
                            line=item.lineno,
                            column=item.col_offset,
                            severity="warning",
                            code=f"Complexity (CC={item.complexity})",
                            message=f"{item.type.capitalize()} '{item.name}' has complexity {item.complexity} (max: {max_complexity})",
                            suggestion="Consider breaking into smaller functions or simplifying logic"
                        )
                        issues.append(issue)
                    
                    # Check function length
                    if item.type in ["function", "method"]:
                        func_length = item.endline - item.lineno if hasattr(item, 'endline') else 0
                        
                        if func_length > max_function_length:
                            issue = self.create_issue(
                                file_path=file_path,
                                line=item.lineno,
                                column=item.col_offset,
                                severity="info",
                                code=f"FunctionLength ({func_length} lines)",
                                message=f"Function '{item.name}' is {func_length} lines long (max: {max_function_length})",
                                suggestion="Consider breaking into smaller functions"
                            )
                            issues.append(issue)
            except Exception as e:
                pass  # Skip complexity check if it fails
            
            # Check maintainability index
            try:
                mi_results = mi_visit(code, multi=True)
                for mi_score in mi_results:
                    rank = mi_rank(mi_score)
                    if rank in ['C', 'D', 'E', 'F']:  # Low maintainability
                        issue = self.create_issue(
                            file_path=file_path,
                            line=0,
                            column=0,
                            severity="warning",
                            code=f"Maintainability (Rank: {rank})",
                            message=f"File has low maintainability index (Rank: {rank}, Score: {mi_score:.1f})",
                            suggestion="Refactor to improve code maintainability"
                        )
                        issues.append(issue)
            except Exception:
                pass  # Skip maintainability check if it fails
        
        except Exception as e:
            issues.append(self.create_issue(
                file_path=file_path,
                line=0,
                column=0,
                severity="error",
                code="Complexity (Error)",
                message=f"Failed to analyze complexity: {str(e)}"
            ))
        
        return issues

