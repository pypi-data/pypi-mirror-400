#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""MCP Server implementation for Python Code Guardian."""

import asyncio
import logging
from typing import Any, Dict, List

from mcp.server import Server
from mcp.types import Tool, TextContent

from .config.config_loader import ConfigLoader
from .reporter import Reporter
from .utils.checker_factory import create_checkers

logger = logging.getLogger(__name__)


class CodeGuardianServer:
    """MCP Server for code quality checks."""

    def __init__(self):
        """Initialize the Code Guardian server."""
        self.server = Server("python-code-guardian")
        self.config_loader = ConfigLoader()
        self.reporter = Reporter()
        self.last_check_results = None
        
        # Initialize checkers using shared factory
        self.checkers = create_checkers()
        
        self._register_handlers()

    def _register_handlers(self):
        """Register MCP tool handlers."""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="check_code",
                    description=(
                        "Run code quality checks on specified files or directories. "
                        "Checks include linting, complexity, typos, structure, coverage, and duplicates."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "File or directory path to check"
                            },
                            "checks": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Specific checks to run (lint, complexity, typo, structure, coverage, duplicates)",
                            },
                            "fix": {
                                "type": "boolean",
                                "description": "Attempt to auto-fix issues",
                            },
                            "config_path": {
                                "type": "string",
                                "description": "Path to custom configuration file",
                            }
                        },
                        "required": ["path"]
                    }
                ),
                Tool(
                    name="get_report",
                    description="Get detailed or summary report of the last code check",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "format": {
                                "type": "string",
                                "enum": ["detailed", "summary"],
                                "description": "Report format",
                            }
                        }
                    }
                ),
                Tool(
                    name="validate_pr",
                    description="Validate all changes in a pull request",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "base_branch": {
                                "type": "string",
                                "description": "Base branch to compare against",
                            },
                            "pr_branch": {
                                "type": "string",
                                "description": "PR branch with changes"
                            },
                            "config_path": {
                                "type": "string",
                                "description": "Path to custom configuration file",
                            }
                        },
                        "required": ["pr_branch"]
                    }
                ),
                Tool(
                    name="configure_rules",
                    description="Update or view current configuration rules",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": ["get", "set"],
                                "description": "Get current config or set new config",
                            },
                            "rules": {
                                "type": "object",
                                "description": "Rules configuration object (required for 'set' action)"
                            }
                        },
                        "required": ["action"]
                    }
                ),
                Tool(
                    name="fix_issues",
                    description="Automatically fix detected issues where possible",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "File or directory path to fix"
                            },
                            "issue_types": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Types of issues to fix (default: all fixable)",
                            }
                        },
                        "required": ["path"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls."""
            try:
                if name == "check_code":
                    return await self._handle_check_code(arguments)
                elif name == "get_report":
                    return await self._handle_get_report(arguments)
                elif name == "validate_pr":
                    return await self._handle_validate_pr(arguments)
                elif name == "configure_rules":
                    return await self._handle_configure_rules(arguments)
                elif name == "fix_issues":
                    return await self._handle_fix_issues(arguments)
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
            except Exception as e:
                logger.error(f"Error handling tool call {name}: {e}", exc_info=True)
                return [TextContent(
                    type="text",
                    text=f"Error executing {name}: {str(e)}"
                )]

    async def _handle_check_code(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle check_code tool call."""
        path = args["path"]
        checks_to_run = args.get("checks", list(self.checkers.keys()))
        fix = args.get("fix", False)
        config_path = args.get("config_path")
        
        # Load configuration
        config = self.config_loader.load_config(config_path)
        
        # Run checks
        results = await self._run_checks(path, checks_to_run, config, fix)
        self.last_check_results = results
        
        # Generate report
        report = self.reporter.generate_detailed_report(results)
        
        return [TextContent(type="text", text=report)]

    async def _handle_get_report(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle get_report tool call."""
        if not self.last_check_results:
            return [TextContent(
                type="text",
                text="No check results available. Run 'check_code' first."
            )]
        
        format_type = args.get("format", "detailed")
        
        if format_type == "summary":
            report = self.reporter.generate_summary_report(self.last_check_results)
        else:
            report = self.reporter.generate_detailed_report(self.last_check_results)
        
        return [TextContent(type="text", text=report)]

    async def _handle_validate_pr(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle validate_pr tool call."""
        base_branch = args.get("base_branch", "main")
        pr_branch = args["pr_branch"]
        config_path = args.get("config_path")
        
        # Load configuration
        config = self.config_loader.load_config(config_path)
        
        # Get changed files
        from .utils.git_utils import get_changed_files
        changed_files = get_changed_files(base_branch, pr_branch)
        
        if not changed_files:
            return [TextContent(
                type="text",
                text="No Python files changed in this PR."
            )]
        
        # Run checks on changed files
        results = {"files": {}, "summary": {"total_issues": 0, "errors": 0, "warnings": 0, "info": 0}}
        for file_path in changed_files:
            if file_path.endswith('.py'):
                file_results = await self._run_checks(
                    file_path, 
                    list(self.checkers.keys()), 
                    config,
                    False
                )
                results["files"][file_path] = file_results
                
                # Aggregate summary
                results["summary"]["total_issues"] += file_results["summary"]["total_issues"]
                results["summary"]["errors"] += file_results["summary"]["errors"]
                results["summary"]["warnings"] += file_results["summary"]["warnings"]
                results["summary"]["info"] += file_results["summary"]["info"]
        
        self.last_check_results = results
        
        # Generate PR validation report
        report = self.reporter.generate_pr_report(results, changed_files)
        
        return [TextContent(type="text", text=report)]

    async def _handle_configure_rules(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle configure_rules tool call."""
        action = args.get("action", "get")
        
        if action == "get":
            current_config = self.config_loader.get_current_config()
            return [TextContent(
                type="text",
                text=f"Current Configuration:\n\n```yaml\n{self.config_loader.config_to_yaml(current_config)}\n```"
            )]
        elif action == "set":
            rules = args.get("rules")
            if not rules:
                return [TextContent(
                    type="text",
                    text="Error: 'rules' parameter required for 'set' action"
                )]
            
            self.config_loader.update_config(rules)
            return [TextContent(
                type="text",
                text="Configuration updated successfully"
            )]

    async def _handle_fix_issues(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handle fix_issues tool call."""
        path = args["path"]
        issue_types = args.get("issue_types", ["lint", "typo"])
        
        fixed_issues = []
        
        for issue_type in issue_types:
            if issue_type in self.checkers:
                checker = self.checkers[issue_type]
                if hasattr(checker, 'fix'):
                    fixes = await checker.fix(path)
                    fixed_issues.extend(fixes)
        
        if fixed_issues:
            report = f"Fixed {len(fixed_issues)} issues:\n\n"
            for fix in fixed_issues:
                report += f"✓ {fix}\n"
        else:
            report = "No auto-fixable issues found."
        
        return [TextContent(type="text", text=report)]

    async def _run_checks(
        self,
        path: str,
        checks_to_run: List[str],
        config: Dict[str, Any],
        fix: bool = False
    ) -> Dict[str, Any]:
        """Run specified checks on the given path."""
        results = {
            "path": path,
            "checks": {},
            "summary": {
                "total_issues": 0,
                "errors": 0,
                "warnings": 0,
                "info": 0
            }
        }
        
        for check_name in checks_to_run:
            if check_name in self.checkers:
                checker = self.checkers[check_name]
                check_config = config.get("rules", {}).get(check_name, {})
                
                if check_config.get("enabled", True):
                    try:
                        check_results = await checker.check(path, check_config)
                        results["checks"][check_name] = check_results
                        
                        # Update summary
                        for issue in check_results.get("issues", []):
                            results["summary"]["total_issues"] += 1
                            severity = issue.get("severity", "info")
                            if severity in results["summary"]:
                                results["summary"][severity] += 1
                    except Exception as e:
                        logger.error(f"Error running {check_name} checker: {e}")
                        results["checks"][check_name] = {
                            "error": str(e),
                            "issues": []
                        }
        
        return results

    async def run(self):
        """Run the MCP server."""
        from mcp.server.stdio import stdio_server
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


def create_server() -> CodeGuardianServer:
    """Create and return a Code Guardian server instance."""
    return CodeGuardianServer()


async def main():
    """Main entry point for the MCP server."""
    logging.basicConfig(level=logging.INFO)
    server = create_server()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())

