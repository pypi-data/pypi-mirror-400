"""Duplicate code detection checker."""

import hashlib
from typing import Any, Dict, List, Tuple
from collections import defaultdict

from .base_checker import BaseChecker


class DuplicateChecker(BaseChecker):
    """Checker for duplicate code blocks."""

    async def check(self, path: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check for duplicate code blocks.
        
        Args:
            path: File or directory path to check
            config: Configuration including min_lines for duplicates
            
        Returns:
            Dictionary containing duplicate code issues
        """
        files = self.get_python_files(path)
        
        if not files:
            return {"issues": [], "stats": {"files_checked": 0, "total_issues": 0}}
        
        min_lines = config.get("min_lines", 6)
        ignore_patterns = config.get("ignore_patterns", [])
        
        # Build a map of code blocks to their locations
        code_blocks = defaultdict(list)
        
        for file_path in files:
            # Skip ignored patterns
            if any(pattern in file_path for pattern in ignore_patterns):
                continue
            
            blocks = await self._extract_code_blocks(file_path, min_lines)
            for block_hash, (start_line, end_line, content) in blocks.items():
                code_blocks[block_hash].append((file_path, start_line, end_line, content))
        
        # Find duplicates
        issues = []
        seen_duplicates = set()
        
        for block_hash, locations in code_blocks.items():
            if len(locations) > 1:
                # Sort by file path and line number
                locations = sorted(locations, key=lambda x: (x[0], x[1]))
                
                for i, (file_path, start_line, end_line, content) in enumerate(locations):
                    # Create a unique key for this duplicate
                    dup_key = (block_hash, file_path, start_line)
                    if dup_key in seen_duplicates:
                        continue
                    seen_duplicates.add(dup_key)
                    
                    # Get other locations
                    other_locations = [
                        f"{loc[0]}:line {loc[1]}"
                        for j, loc in enumerate(locations)
                        if j != i
                    ]
                    
                    num_lines = end_line - start_line + 1
                    issue = self.create_issue(
                        file_path=file_path,
                        line=start_line,
                        column=0,
                        severity="warning",
                        code=f"Duplicate ({num_lines} lines)",
                        message=f"Duplicate code block found ({num_lines} lines)",
                        suggestion=f"Consider extracting to a shared function. Also in: {', '.join(other_locations[:2])}"
                    )
                    issues.append(issue)
        
        return {
            "issues": issues,
            "stats": {
                "files_checked": len(files),
                "total_issues": len(issues),
                "duplicate_groups": len([locs for locs in code_blocks.values() if len(locs) > 1])
            }
        }

    async def _extract_code_blocks(
        self,
        file_path: str,
        min_lines: int
    ) -> Dict[str, Tuple[int, int, str]]:
        """Extract code blocks from a file and hash them."""
        blocks = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Extract blocks of min_lines or more
            for start_idx in range(len(lines) - min_lines + 1):
                end_idx = start_idx + min_lines
                
                # Get block content
                block_lines = lines[start_idx:end_idx]
                
                # Normalize: remove leading/trailing whitespace, skip blank lines and comments
                normalized_lines = []
                for line in block_lines:
                    stripped = line.strip()
                    if stripped and not stripped.startswith('#'):
                        # Remove leading whitespace for comparison
                        normalized_lines.append(stripped)
                
                if len(normalized_lines) >= min_lines // 2:  # At least half should be code
                    # Create hash of normalized content
                    content = '\n'.join(normalized_lines)
                    block_hash = hashlib.md5(content.encode()).hexdigest()
                    
                    # Store first occurrence of this hash
                    if block_hash not in blocks:
                        blocks[block_hash] = (start_idx + 1, end_idx, content)
        
        except Exception:
            pass  # Skip files that can't be read
        
        return blocks

