"""Go language - Style/Taste patterns."""

import re

from deeplint.patterns.base import RegexPattern, Severity


class GoOverconfidentComment(RegexPattern):
    """Detect overconfident comments in Go."""

    id = "go_overconfident_comment"
    severity = Severity.MEDIUM
    axis = "style"
    message = "Overconfident comment - code should speak for itself"
    pattern = re.compile(
        r"//\s*(obviously|clearly|simply|just|easy|trivial|of course)\b",
        re.IGNORECASE,
    )


class GoHedgingComment(RegexPattern):
    """Detect hedging/uncertain comments in Go."""

    id = "go_hedging_comment"
    severity = Severity.HIGH
    axis = "style"
    message = "Hedging comment indicates AI uncertainty - verify implementation"
    pattern = re.compile(
        r"//\s*(should work|hopefully|probably|might|try this|i think)\b",
        re.IGNORECASE,
    )


class GoPythonPatterns(RegexPattern):
    """Detect Python patterns leaked into Go code."""

    id = "go_python_pattern"
    severity = Severity.HIGH
    axis = "style"
    message = "Python pattern in Go code - use Go idioms"
    # Only detecting Python-specific method patterns that are invalid in Go
    pattern = re.compile(
        r"(\.append\(|\.split\(|\.join\()",
        re.IGNORECASE,
    )


GO_STYLE_PATTERNS = [
    GoOverconfidentComment(),
    GoHedgingComment(),
    GoPythonPatterns(),
]
