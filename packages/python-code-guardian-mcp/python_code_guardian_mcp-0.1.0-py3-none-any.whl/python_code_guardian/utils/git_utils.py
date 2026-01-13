"""Git utility functions for PR validation."""

import subprocess
from typing import List


def get_changed_files(base_branch: str, pr_branch: str) -> List[str]:
    """
    Get list of changed Python files between two branches.
    
    Args:
        base_branch: Base branch name
        pr_branch: PR branch name
        
    Returns:
        List of changed file paths
    """
    try:
        # Get diff between branches
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{base_branch}...{pr_branch}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            files = result.stdout.strip().split('\n')
            # Filter for Python files
            python_files = [f for f in files if f.endswith('.py')]
            return python_files
    
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass  # Git not available or timeout
    
    return []


def is_git_repository() -> bool:
    """Check if current directory is a git repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

