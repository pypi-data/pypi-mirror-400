"""JavaScript/TypeScript - Structural anti-patterns."""

import re

from deeplint.patterns.base import RegexPattern, Severity


class JSMissingErrorHandling(RegexPattern):
    """Detect potential missing error handling for promises."""

    id = "js_missing_error_handling"
    severity = Severity.MEDIUM
    axis = "structure"
    message = "Potential missing error handling for promise - consider adding try/catch or .catch()"
    pattern = re.compile(
        r"(fetch|axios|http)\s*\(",
    )


JS_STRUCTURE_PATTERNS = [
    JSMissingErrorHandling(),
]
