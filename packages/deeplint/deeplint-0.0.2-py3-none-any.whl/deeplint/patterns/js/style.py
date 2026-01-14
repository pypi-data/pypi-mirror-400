"""JavaScript/TypeScript - Style/Taste patterns."""

import re

from deeplint.patterns.base import RegexPattern, Severity


class JSOverconfidentComment(RegexPattern):
    """Detect overconfident comments in JS/TS."""

    id = "js_overconfident_comment"
    severity = Severity.MEDIUM
    axis = "style"
    message = "Overconfident comment - code should speak for itself"
    pattern = re.compile(
        r"//\s*(obviously|clearly|simply|just|easy|trivial|of course)\b",
        re.IGNORECASE,
    )


class JSHedgingComment(RegexPattern):
    """Detect hedging/uncertain comments in JS/TS."""

    id = "js_hedging_comment"
    severity = Severity.HIGH
    axis = "style"
    message = "Hedging comment indicates AI uncertainty - verify implementation"
    pattern = re.compile(
        r"//\s*(should work|hopefully|probably|might|try this|i think)\b",
        re.IGNORECASE,
    )


class JSPythonPatterns(RegexPattern):
    """Detect Python patterns leaked into JS/TS code."""

    id = "js_python_pattern"
    severity = Severity.HIGH
    axis = "style"
    message = "Python pattern in JS/TS code - use JavaScript idioms"
    # Only detecting patterns that are clearly Python-specific and invalid in JS
    pattern = re.compile(
        r"(\.append\()",
        re.IGNORECASE,
    )


class JSVarKeyword(RegexPattern):
    """Detect outdated var keyword in JS/TS."""

    id = "js_var_keyword"
    severity = Severity.MEDIUM
    axis = "style"
    message = "Use 'const' or 'let' instead of 'var'"
    pattern = re.compile(r"\bvar\s+\w+\s*=")


class JSUnnecessaryIIFE(RegexPattern):
    """Detect unnecessary IIFE wrappers - AI over-engineering."""

    id = "js_unnecessary_iife"
    severity = Severity.MEDIUM
    axis = "style"
    message = "Unnecessary IIFE wrapper - AI over-engineering a simple async call"
    # Simplified pattern to match const x = (async () =>
    pattern = re.compile(
        r"const\s+\w+\s*=\s*\(\s*async\s*\(\)",
    )


class JSNestedTernaryAbuse(RegexPattern):
    """Detect nested ternary hell - overly complex conditionals."""

    id = "js_nested_ternary_abuse"
    severity = Severity.MEDIUM
    axis = "style"
    message = "Nested ternary hell - extract to switch statement or lookup object"
    # Simplified to detect multiple ? : on same line
    pattern = re.compile(
        r"\?[^:?]+:[^:?]+\?[^:?]+:",
    )


class JSMagicCSSValue(RegexPattern):
    """Detect hardcoded magic CSS values."""

    id = "js_magic_css_value"
    severity = Severity.LOW
    axis = "style"
    message = "Magic CSS value - extract to design token or const"
    pattern = re.compile(
        r"\b(\d{3,4}px|#\w{6}|rgba?\([^)]+\)|hsl\(\d+)",
    )


JS_STYLE_PATTERNS = [
    JSOverconfidentComment(),
    JSHedgingComment(),
    JSPythonPatterns(),
    JSVarKeyword(),
    JSUnnecessaryIIFE(),
    JSNestedTernaryAbuse(),
    JSMagicCSSValue(),
]
