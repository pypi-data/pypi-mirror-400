"""Factory for creating and managing code checkers."""

from typing import Dict

from ..checkers import (
    ComplexityChecker,
    CoverageChecker,
    DuplicateChecker,
    LintChecker,
    StructureChecker,
    TypoChecker,
)


def create_checkers() -> Dict[str, object]:
    """Create and return a dictionary of all available checkers.
    
    Returns:
        Dictionary mapping checker names to checker instances.
    """
    return {
        "lint": LintChecker(),
        "complexity": ComplexityChecker(),
        "typo": TypoChecker(),
        "structure": StructureChecker(),
        "coverage": CoverageChecker(),
        "duplicates": DuplicateChecker(),
    }


