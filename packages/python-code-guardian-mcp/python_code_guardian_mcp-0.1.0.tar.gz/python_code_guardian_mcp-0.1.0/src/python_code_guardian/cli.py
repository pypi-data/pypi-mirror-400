"""Command-line interface for Python Code Guardian."""

import asyncio
import sys
from pathlib import Path

import click

from .config.config_loader import ConfigLoader
from .reporter import Reporter
from .utils.checker_factory import create_checkers


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Python Code Guardian - Comprehensive code quality checks for Python projects."""
    pass


@cli.command()
@click.option('--path', '-p', required=True, help='File or directory to check')
@click.option('--checks', '-c', multiple=True, help='Specific checks to run')
@click.option('--fix', is_flag=True, help='Attempt to auto-fix issues')
@click.option('--config', '-cfg', help='Path to configuration file')
@click.option('--format', '-f', type=click.Choice(['detailed', 'summary']), default='detailed', help='Report format')
def check(path, checks, fix, config, format):
    """Run code quality checks on specified path."""
    click.echo(f"🔍 Checking code quality for: {path}")
    
    # Load configuration
    config_loader = ConfigLoader()
    cfg = config_loader.load_config(config)
    
    # Initialize checkers using shared factory
    available_checkers = create_checkers()
    
    checks_to_run = list(checks) if checks else list(available_checkers.keys())
    
    # Run checks
    results = {
        "path": path,
        "checks": {},
        "summary": {"total_issues": 0, "errors": 0, "warnings": 0, "info": 0}
    }
    
    for check_name in checks_to_run:
        if check_name in available_checkers:
            checker = available_checkers[check_name]
            check_config = cfg.get("rules", {}).get(check_name, {})
            
            if check_config.get("enabled", True):
                click.echo(f"  Running {check_name} checks...")
                check_results = asyncio.run(checker.check(path, check_config))
                results["checks"][check_name] = check_results
                
                # Update summary
                for issue in check_results.get("issues", []):
                    results["summary"]["total_issues"] += 1
                    severity = issue.get("severity", "info")
                    if severity in results["summary"]:
                        results["summary"][severity] += 1
    
    # Generate report
    reporter = Reporter()
    if format == 'summary':
        report = reporter.generate_summary_report(results)
    else:
        report = reporter.generate_detailed_report(results)
    
    click.echo("\n" + report)
    
    # Exit with error code if issues found
    if results["summary"]["total_issues"] > 0:
        sys.exit(1)


@cli.command()
@click.option('--format', '-f', type=click.Choice(['detailed', 'summary']), default='detailed', help='Report format')
def report(format):
    """Display the last check report."""
    click.echo("No previous check results available. Run 'check' command first.")


@cli.command()
@click.option('--base', '-b', default='main', help='Base branch')
@click.option('--pr', '-p', required=True, help='PR branch')
@click.option('--config', '-cfg', help='Path to configuration file')
def validate_pr(base, pr, config):
    """Validate changes in a pull request."""
    from .utils.git_utils import get_changed_files, is_git_repository
    
    if not is_git_repository():
        click.echo("❌ Error: Not a git repository", err=True)
        sys.exit(1)
    
    click.echo(f"🔍 Validating PR: {pr} against {base}")
    
    changed_files = get_changed_files(base, pr)
    
    if not changed_files:
        click.echo("✓ No Python files changed")
        return
    
    click.echo(f"Found {len(changed_files)} changed Python file(s)")
    
    # Load configuration
    config_loader = ConfigLoader()
    cfg = config_loader.load_config(config)
    
    # Initialize checkers using shared factory
    available_checkers = create_checkers()
    
    # Run checks on changed files
    results = {
        "files": {},
        "summary": {"total_issues": 0, "errors": 0, "warnings": 0, "info": 0}
    }
    
    for file_path in changed_files:
        if file_path.endswith('.py'):
            click.echo(f"  Checking {file_path}...")
            file_results = {
                "path": file_path,
                "checks": {},
                "summary": {"total_issues": 0, "errors": 0, "warnings": 0, "info": 0}
            }
            
            for check_name in available_checkers.keys():
                checker = available_checkers[check_name]
                check_config = cfg.get("rules", {}).get(check_name, {})
                
                if check_config.get("enabled", True):
                    try:
                        check_results = asyncio.run(checker.check(file_path, check_config))
                        file_results["checks"][check_name] = check_results
                        
                        # Update file summary
                        for issue in check_results.get("issues", []):
                            file_results["summary"]["total_issues"] += 1
                            severity = issue.get("severity", "info")
                            if severity in file_results["summary"]:
                                file_results["summary"][severity] += 1
                    except Exception as e:
                        click.echo(f"    Warning: Error running {check_name}: {e}", err=True)
            
            results["files"][file_path] = file_results
            
            # Aggregate summary
            results["summary"]["total_issues"] += file_results["summary"]["total_issues"]
            results["summary"]["errors"] += file_results["summary"]["errors"]
            results["summary"]["warnings"] += file_results["summary"]["warnings"]
            results["summary"]["info"] += file_results["summary"]["info"]
    
    # Generate report
    reporter = Reporter()
    report = reporter.generate_pr_report(results, changed_files)
    click.echo("\n" + report)
    
    # Exit with error code if issues found
    if results["summary"]["total_issues"] > 0:
        sys.exit(1)
    
    click.echo("✓ PR validation complete")


@cli.command()
def install_hook():
    """Install pre-commit hook for this project."""
    import subprocess
    
    click.echo("📦 Installing pre-commit hook...")
    
    # Create .pre-commit-config.yaml
    pre_commit_config = """repos:
  - repo: local
    hooks:
      - id: python-code-guardian
        name: Python Code Guardian
        entry: python-code-guardian check --path .
        language: system
        types: [python]
        pass_filenames: false
"""
    
    config_path = Path(".pre-commit-config.yaml")
    if config_path.exists():
        click.echo("⚠ .pre-commit-config.yaml already exists")
        if not click.confirm("Overwrite?"):
            return
    
    with open(config_path, 'w') as f:
        f.write(pre_commit_config)
    
    # Install pre-commit
    try:
        subprocess.run(["pre-commit", "install"], check=True)
        click.echo("✓ Pre-commit hook installed successfully")
    except subprocess.CalledProcessError:
        click.echo("❌ Failed to install pre-commit hook", err=True)
        sys.exit(1)
    except FileNotFoundError:
        click.echo("❌ pre-commit not found. Install it with: pip install pre-commit", err=True)
        sys.exit(1)


@cli.command()
@click.option('--output', '-o', default='.code-guardian.yaml', help='Output file path')
def init_config(output):
    """Initialize a new configuration file."""
    config_loader = ConfigLoader()
    
    if Path(output).exists():
        if not click.confirm(f"{output} already exists. Overwrite?"):
            return
    
    if config_loader.save_config(output):
        click.echo(f"✓ Configuration file created: {output}")
    else:
        click.echo(f"❌ Failed to create configuration file", err=True)
        sys.exit(1)


def main():
    """Entry point for CLI."""
    cli()


if __name__ == "__main__":
    main()

