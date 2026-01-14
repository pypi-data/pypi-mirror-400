"""Go language - Information Utility (Noise) patterns."""

import re

from deeplint.patterns.base import RegexPattern, Severity


class GoDebugPrint(RegexPattern):
    """Detect debug print statements in Go."""

    id = "go_debug_print"
    severity = Severity.MEDIUM
    axis = "noise"
    message = "Debug print statement - remove before production"
    pattern = re.compile(r'\bfmt\.Print(ln|f)?\s*\([^)]*"(debug|DEBUG|test|TEST|temp|TEMP)\b')


class GoTodoComment(RegexPattern):
    """Detect TODO comments in Go."""

    id = "go_todo_comment"
    severity = Severity.LOW
    axis = "noise"
    message = "TODO comment - track in issue tracker instead"
    pattern = re.compile(r"//\s*(TODO|FIXME|XXX|HACK)\s*:", re.IGNORECASE)


class GoRedundantComment(RegexPattern):
    """Detect redundant comments in Go."""

    id = "go_redundant_comment"
    severity = Severity.MEDIUM
    axis = "noise"
    message = "Redundant comment restating obvious code"
    pattern = re.compile(
        r"//\s*(increment|decrement|set|assign|return|get|initialize|init|create)\s+\w+\s*$",
        re.IGNORECASE,
    )


GO_NOISE_PATTERNS = [
    GoDebugPrint(),
    GoTodoComment(),
    GoRedundantComment(),
]
