"""JavaScript/TypeScript - Information Utility (Noise) patterns."""

import re

from deeplint.patterns.base import RegexPattern, Severity


class JSDebugConsole(RegexPattern):
    """Detect debug console statements in JS/TS."""

    id = "js_debug_console"
    severity = Severity.MEDIUM
    axis = "noise"
    message = "Debug console statement - remove before production"
    pattern = re.compile(
        r'\bconsole\.(log|debug|info|warn|error)\s*\([^)]*["\']?(debug|DEBUG|test|TEST|temp|TEMP)\b'
    )


class JSTodoComment(RegexPattern):
    """Detect TODO comments in JS/TS."""

    id = "js_todo_comment"
    severity = Severity.LOW
    axis = "noise"
    message = "TODO comment - track in issue tracker instead"
    pattern = re.compile(r"//\s*(TODO|FIXME|XXX|HACK)\s*:", re.IGNORECASE)


class JSRedundantComment(RegexPattern):
    """Detect redundant comments in JS/TS."""

    id = "js_redundant_comment"
    severity = Severity.MEDIUM
    axis = "noise"
    message = "Redundant comment restating obvious code"
    pattern = re.compile(
        r"//\s*(increment|decrement|set|assign|return|get|initialize|init|create)\s+\w+\s*$",
        re.IGNORECASE,
    )


class JSCommentedCode(RegexPattern):
    """Detect commented-out code in JS/TS."""

    id = "js_commented_code"
    severity = Severity.MEDIUM
    axis = "noise"
    message = "Commented-out code - remove or use version control"
    pattern = re.compile(
        r"//\s*(const|let|var|function|if\s*\(|for\s*\(|while\s*\(|return\s+)",
        re.IGNORECASE,
    )


class JSRedundantSelfExplanatoryComment(RegexPattern):
    """Detect redundant comments explaining variable assignment to itself."""

    id = "js_redundant_self_explanatory_comment"
    severity = Severity.HIGH
    axis = "noise"
    message = "Redundant comment explaining variable assignment to itself - peak AI slop"
    pattern = re.compile(
        r"const\s+(\w+)\s*=\s*\1\s*;?\s*//\s*(?:set|assign|store)\s+\1\b",
        re.IGNORECASE,
    )


class JSExcessiveBoilerplateComment(RegexPattern):
    """Detect boilerplate comments that restate the obvious."""

    id = "js_excessive_boilerplate_comment"
    severity = Severity.MEDIUM
    axis = "noise"
    message = "Boilerplate comment that restates the obvious - adds zero insight"
    pattern = re.compile(
        r"//\s*This (?:function|component|hook|variable|method).* (?:does|is|handles?|returns?|takes?|processes?)",
        re.IGNORECASE,
    )


class JSDebugLogWithComment(RegexPattern):
    """Detect debug logs with apologetic comments."""

    id = "js_debug_log_with_comment"
    severity = Severity.MEDIUM
    axis = "noise"
    message = "Debug log with apologetic comment - AI trying to justify its existence"
    pattern = re.compile(
        r"console\.(log|debug|info)\([^)]+\)\s*;\s*//\s*(?:debug|temp|test|check|log|print)",
        re.IGNORECASE,
    )


class JSProductionConsoleLog(RegexPattern):
    """Detect console logging in production code."""

    id = "js_production_console_log"
    severity = Severity.MEDIUM
    axis = "noise"
    message = "Found console logging in production code - remove before deployment"
    pattern = re.compile(
        r"console\.(log|warn|error|info|debug|trace)\(",
    )


JS_NOISE_PATTERNS = [
    JSDebugConsole(),
    JSTodoComment(),
    JSRedundantComment(),
    JSCommentedCode(),
    JSRedundantSelfExplanatoryComment(),
    JSExcessiveBoilerplateComment(),
    JSDebugLogWithComment(),
    JSProductionConsoleLog(),
]
