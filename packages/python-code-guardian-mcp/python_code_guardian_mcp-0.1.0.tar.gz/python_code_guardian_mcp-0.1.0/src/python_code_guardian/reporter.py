"""Report generator for code quality check results."""

from typing import Any, Dict, List
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)


class Reporter:
    """Generates formatted reports from check results."""

    def generate_detailed_report(self, results: Dict[str, Any]) -> str:
        """
        Generate detailed report with all issues.
        
        Args:
            results: Check results dictionary
            
        Returns:
            Formatted report string
        """
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("CODE QUALITY REPORT")
        report_lines.append("=" * 80)
        report_lines.append("")
        
        # Group issues by file
        if "files" in results:
            # PR validation format
            for file_path, file_results in results["files"].items():
                report_lines.extend(self._format_file_results(file_path, file_results))
        else:
            # Single check format
            report_lines.extend(self._format_file_results(results.get("path", ""), results))
        
        # Add summary
        report_lines.append("-" * 80)
        report_lines.append("SUMMARY STATISTICS")
        report_lines.append("-" * 80)
        report_lines.extend(self._format_summary(results.get("summary", {})))
        report_lines.append("=" * 80)
        
        return "\n".join(report_lines)

    def generate_summary_report(self, results: Dict[str, Any]) -> str:
        """
        Generate summary report with statistics only.
        
        Args:
            results: Check results dictionary
            
        Returns:
            Formatted summary string
        """
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("CODE QUALITY SUMMARY")
        report_lines.append("=" * 80)
        report_lines.extend(self._format_summary(results.get("summary", {})))
        
        # Add check-specific stats
        if "checks" in results:
            report_lines.append("")
            report_lines.append("Issues by Category:")
            for check_name, check_results in results["checks"].items():
                num_issues = len(check_results.get("issues", []))
                if num_issues > 0:
                    report_lines.append(f"  - {check_name.capitalize()}: {num_issues}")
        
        report_lines.append("=" * 80)
        
        return "\n".join(report_lines)

    def generate_pr_report(self, results: Dict[str, Any], changed_files: List[str]) -> str:
        """
        Generate report for PR validation.
        
        Args:
            results: Check results dictionary
            changed_files: List of changed file paths
            
        Returns:
            Formatted PR report string
        """
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("PULL REQUEST VALIDATION REPORT")
        report_lines.append("=" * 80)
        report_lines.append("")
        report_lines.append(f"Changed Files: {len(changed_files)}")
        report_lines.append("")
        
        summary = results.get("summary", {})
        total_issues = summary.get("total_issues", 0)
        
        if total_issues == 0:
            report_lines.append(f"{Fore.GREEN}✓ All checks passed! No issues found.{Style.RESET_ALL}")
        else:
            report_lines.append(f"{Fore.YELLOW}⚠ Found {total_issues} issue(s) in the changed files{Style.RESET_ALL}")
            report_lines.append("")
            
            # Show issues by file
            for file_path, file_results in results.get("files", {}).items():
                file_issues = []
                for check_results in file_results.get("checks", {}).values():
                    file_issues.extend(check_results.get("issues", []))
                
                if file_issues:
                    report_lines.append(f"\n{file_path}:")
                    report_lines.append("-" * 80)
                    for issue in file_issues[:5]:  # Show first 5 issues per file
                        report_lines.append(self._format_issue(issue))
                    
                    if len(file_issues) > 5:
                        report_lines.append(f"  ... and {len(file_issues) - 5} more issue(s)")
        
        report_lines.append("")
        report_lines.append("-" * 80)
        report_lines.extend(self._format_summary(summary))
        report_lines.append("=" * 80)
        
        return "\n".join(report_lines)

    def _format_file_results(self, file_path: str, results: Dict[str, Any]) -> List[str]:
        """Format results for a single file."""
        lines = []
        
        if file_path:
            lines.append(f"FILE: {file_path}")
            lines.append("-" * 80)
        
        # Collect all issues from all checks
        all_issues = []
        if "checks" in results:
            for check_name, check_results in results["checks"].items():
                issues = check_results.get("issues", [])
                all_issues.extend(issues)
        
        # Sort by line number
        all_issues.sort(key=lambda x: (x.get("line", 0), x.get("column", 0)))
        
        # Format each issue
        if all_issues:
            for issue in all_issues:
                lines.append(self._format_issue(issue))
                lines.append("")
        else:
            lines.append(f"{Fore.GREEN}✓ No issues found{Style.RESET_ALL}")
            lines.append("")
        
        return lines

    def _format_issue(self, issue: Dict[str, Any]) -> str:
        """Format a single issue."""
        severity = issue.get("severity", "info")
        line = issue.get("line", 0)
        column = issue.get("column", 0)
        code = issue.get("code", "")
        message = issue.get("message", "")
        suggestion = issue.get("suggestion", "")
        
        # Color code by severity
        severity_colors = {
            "error": Fore.RED,
            "warning": Fore.YELLOW,
            "info": Fore.CYAN
        }
        color = severity_colors.get(severity, "")
        
        # Format issue
        lines = []
        lines.append(f"{color}[{severity.upper()}] Line {line}, Column {column} - {code}{Style.RESET_ALL}")
        lines.append(f"  {message}")
        
        if suggestion:
            lines.append(f"  {Fore.GREEN}💡 Suggestion: {suggestion}{Style.RESET_ALL}")
        
        return "\n".join(lines)

    def _format_summary(self, summary: Dict[str, Any]) -> List[str]:
        """Format summary statistics."""
        lines = []
        
        total_issues = summary.get("total_issues", 0)
        errors = summary.get("errors", 0)
        warnings = summary.get("warnings", 0)
        info = summary.get("info", 0)
        
        lines.append(f"Total Issues: {total_issues}")
        if total_issues > 0:
            lines.append(f"  - {Fore.RED}Errors: {errors}{Style.RESET_ALL}")
            lines.append(f"  - {Fore.YELLOW}Warnings: {warnings}{Style.RESET_ALL}")
            lines.append(f"  - {Fore.CYAN}Info: {info}{Style.RESET_ALL}")
        
        # Add coverage info if available
        if "total_coverage" in summary:
            coverage = summary.get("total_coverage", 0)
            threshold = summary.get("threshold", 75)
            if coverage >= threshold:
                lines.append(f"\n{Fore.GREEN}Test Coverage: {coverage:.1f}% ✓{Style.RESET_ALL}")
            else:
                lines.append(f"\n{Fore.YELLOW}Test Coverage: {coverage:.1f}% (threshold: {threshold}%){Style.RESET_ALL}")
        
        return lines

