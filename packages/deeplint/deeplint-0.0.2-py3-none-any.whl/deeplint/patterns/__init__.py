"""Pattern registry."""

from deeplint.patterns.base import BasePattern
from deeplint.patterns.go import GO_NOISE_PATTERNS, GO_STYLE_PATTERNS
from deeplint.patterns.hallucinations import HALLUCINATION_PATTERNS
from deeplint.patterns.js import (
    JS_HALLUCINATION_PATTERNS,
    JS_NOISE_PATTERNS,
    JS_REACT_PATTERNS,
    JS_STRUCTURE_PATTERNS,
    JS_STYLE_PATTERNS,
    JS_TYPESCRIPT_PATTERNS,
)
from deeplint.patterns.noise import NOISE_PATTERNS
from deeplint.patterns.structure import STRUCTURE_PATTERNS
from deeplint.patterns.style import STYLE_PATTERNS


def get_all_patterns() -> list[BasePattern]:
    """Get all registered patterns."""
    return [
        # Python patterns
        *NOISE_PATTERNS,
        *HALLUCINATION_PATTERNS,
        *STYLE_PATTERNS,
        *STRUCTURE_PATTERNS,
        # Go patterns
        *GO_NOISE_PATTERNS,
        *GO_STYLE_PATTERNS,
        # JavaScript/TypeScript patterns
        *JS_NOISE_PATTERNS,
        *JS_STYLE_PATTERNS,
        *JS_HALLUCINATION_PATTERNS,
        *JS_REACT_PATTERNS,
        *JS_TYPESCRIPT_PATTERNS,
        *JS_STRUCTURE_PATTERNS,
    ]


__all__ = ["get_all_patterns", "BasePattern"]
