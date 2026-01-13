"""Test coverage checker using coverage.py."""

import subprocess
import os
import json
from typing import Any, Dict, List

from .base_checker import BaseChecker


class CoverageChecker(BaseChecker):
    """Checker for test coverage analysis."""

    async def check(self, path: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check test coverage for the specified path.
        
        Args:
            path: File or directory path to check
            config: Configuration including coverage threshold
            
        Returns:
            Dictionary containing coverage issues
        """
        threshold = config.get("test_coverage_threshold", 75)
        
        issues = []
        coverage_data = await self._get_coverage(path)
        
        if coverage_data:
            total_coverage = coverage_data.get("totals", {}).get("percent_covered", 0)
            
            if total_coverage < threshold:
                issue = self.create_issue(
                    file_path=path,
                    line=0,
                    column=0,
                    severity="warning",
                    code=f"Coverage ({total_coverage:.1f}%)",
                    message=f"Test coverage is {total_coverage:.1f}% (threshold: {threshold}%)",
                    suggestion=f"Add tests to increase coverage to at least {threshold}%"
                )
                issues.append(issue)
            
            # Check individual files with low coverage
            for file_path, file_data in coverage_data.get("files", {}).items():
                file_coverage = file_data.get("summary", {}).get("percent_covered", 0)
                
                if file_coverage < threshold:
                    missing_lines = file_data.get("missing_lines", [])
                    issue = self.create_issue(
                        file_path=file_path,
                        line=0,
                        column=0,
                        severity="info",
                        code=f"Coverage ({file_coverage:.1f}%)",
                        message=f"File coverage is {file_coverage:.1f}% (threshold: {threshold}%)",
                        suggestion=f"Add tests for lines: {self._format_line_ranges(missing_lines)}"
                    )
                    issues.append(issue)
        
        return {
            "issues": issues,
            "stats": {
                "total_coverage": coverage_data.get("totals", {}).get("percent_covered", 0) if coverage_data else 0,
                "threshold": threshold
            }
        }

    async def _get_coverage(self, path: str) -> Dict[str, Any]:
        """Run coverage analysis and return results."""
        try:
            # Check if .coverage file exists or if pytest-cov is available
            coverage_file = os.path.join(os.path.dirname(path) if os.path.isfile(path) else path, ".coverage")
            
            # Try to run coverage
            if os.path.exists(coverage_file):
                # Generate JSON report from existing coverage data
                result = subprocess.run(
                    ["coverage", "json", "-o", "/tmp/coverage.json"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0 and os.path.exists("/tmp/coverage.json"):
                    with open("/tmp/coverage.json", 'r') as f:
                        return json.load(f)
            else:
                # Try to run tests with coverage
                if os.path.isdir(path):
                    test_dir = os.path.join(path, "tests")
                    if os.path.exists(test_dir):
                        result = subprocess.run(
                            ["pytest", "--cov=" + path, "--cov-report=json:/tmp/coverage.json", test_dir],
                            capture_output=True,
                            text=True,
                            timeout=60
                        )
                        
                        if os.path.exists("/tmp/coverage.json"):
                            with open("/tmp/coverage.json", 'r') as f:
                                return json.load(f)
        
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            pass  # Coverage check failed
        
        return None

    def _format_line_ranges(self, lines: List[int]) -> str:
        """Format list of line numbers into ranges."""
        if not lines:
            return "none"
        
        if len(lines) > 10:
            return f"{lines[0]}-{lines[-1]} ({len(lines)} lines)"
        
        ranges = []
        start = lines[0]
        end = lines[0]
        
        for line in lines[1:]:
            if line == end + 1:
                end = line
            else:
                if start == end:
                    ranges.append(str(start))
                else:
                    ranges.append(f"{start}-{end}")
                start = end = line
        
        if start == end:
            ranges.append(str(start))
        else:
            ranges.append(f"{start}-{end}")
        
        return ", ".join(ranges)

