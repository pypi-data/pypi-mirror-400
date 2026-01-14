# DeepLint - AI Code Anti-Pattern Detector

<!-- Thanks to: @rsionnach/sloppylint for inspiration -->

## Overview

DeepLint is a multi-language static analysis tool that detects AI-generated code anti-patterns. It catches issues that traditional linters miss, such as hallucinated imports, mutable default arguments, cross-language pattern leakage, and placeholder code.

**Supported Languages**: Python, Go, JavaScript, TypeScript

## Installation

```bash
pip install deeplint
```

## Basic Usage

### Scan Current Directory
```bash
deeplint .
```

### Scan Specific Directory or File
```bash
deeplint src/
deeplint path/to/file.py
```

### Scan Multiple Paths
```bash
deeplint src/ tests/ scripts/
```

## Command Options

### Language Selection
```bash
# Scan only Python files
deeplint src/ --language python

# Scan multiple specific languages
deeplint src/ --language javascript,typescript

# Auto-detect all languages (default)
deeplint src/
```

### Severity Filtering
```bash
# Only show critical and high severity issues
deeplint src/ --severity high
deeplint src/ --lenient

# Show all severity levels
deeplint src/ --strict

# Filter to specific severity
deeplint src/ --severity critical
```

### Output Formats
```bash
# Detailed output (default)
deeplint src/ --format detailed

# Compact output
deeplint src/ --format compact

# JSON output
deeplint src/ --format json

# Save to file
deeplint src/ --output report.json
```

### CI/CD Integration
```bash
# Exit with code 1 if any issues found
deeplint src/ --ci

# Exit with code 1 if score exceeds threshold
deeplint src/ --max-score 50

# Combine filters for CI
deeplint src/ --ci --severity high --max-score 100
```

### Filtering and Exclusions
```bash
# Ignore specific patterns (glob)
deeplint src/ --ignore "tests/*" --ignore "migrations/*"

# Disable specific pattern checks
deeplint src/ --disable magic_number --disable debug_print
```

## Detection Strategies

### Pattern Categories

DeepLint organizes detections into four axes:

1. **Noise** (Information Utility)
   - Debug prints and logging
   - Redundant comments
   - Commented-out code
   - Obvious type annotations

2. **Lies** (Information Quality)
   - Hallucinated imports (non-existent packages)
   - Wrong API usage
   - Placeholder code (TODO, pass, ...)
   - Mutable default arguments
   - Assumption comments

3. **Soul** (Style/Taste)
   - Overconfident comments ("obviously", "clearly")
   - Hedging comments ("should work", "hopefully")
   - God functions (too long, too complex)
   - Deep nesting
   - Single-letter variables

4. **Structure** (Anti-patterns)
   - Bare except clauses
   - Unused imports
   - Dead code
   - Duplicate code
   - Single-method classes

### Scoring System

DeepLint assigns scores based on severity:
- **Critical**: 30 points (e.g., bare except, mutable defaults)
- **High**: 15 points (e.g., hallucinated imports, placeholders)
- **Medium**: 8 points (e.g., unused imports, hedging comments)
- **Low**: 3 points (e.g., TODO comments, obvious comments)

**Verdict Levels**:
- 0-50 pts: CLEAN
- 51-150 pts: ACCEPTABLE
- 151-300 pts: SLOPPY
- 300+ pts: DISASTER

### Language-Specific Patterns

#### Python
- AST-based detection for structural issues
- Import validation
- Cross-language pattern detection (JS/Java/Ruby patterns in Python)

#### JavaScript/TypeScript
- React hooks anti-patterns
- TypeScript `any` type abuse
- Hallucinated Next.js imports
- Missing error handling

#### Go
- Debug print statements
- Python patterns leaked into Go code

## Usage Strategies

### Development Workflow
```bash
# Quick check before commit
deeplint src/ --severity high

# Full analysis
deeplint .

# Focus on specific file being edited
deeplint src/api.py --strict
```

### Code Review
```bash
# Check PR changes with high bar
deeplint src/ --ci --severity high --max-score 50

# Generate review report
deeplint src/ --format json --output review.json
```

### CI Pipeline
```yaml
# Example GitHub Actions
- name: Run DeepLint
  run: |
    pip install deeplint
    deeplint src/ --ci --severity high --max-score 100
```

### Progressive Adoption
```bash
# Start with critical issues only
deeplint src/ --severity critical

# Gradually tighten
deeplint src/ --severity high

# Eventually go strict
deeplint src/ --strict --max-score 50
```

## Configuration

Create `pyproject.toml` in your project root:

```toml
[tool.deeplint]
# Paths to ignore
ignore = ["tests/*", "migrations/*", ".venv/*"]

# Patterns to disable
disable = ["magic_number", "debug_print"]

# Default severity filter
severity = "medium"

# Maximum acceptable score
max-score = 100

# CI mode
ci = false

# Output format
format = "detailed"
```

Then simply run:
```bash
deeplint .
```

## Common Patterns Detected

### Critical Issues
```python
# Mutable default argument
def process(items=[]):  # ❌ Shared state bug
    items.append(1)

# Bare except
try:
    risky_operation()
except:  # ❌ Catches SystemExit!
    pass
```

### High Severity
```python
# Hallucinated import
from requests import fetch  # ❌ requests has no fetch

# Placeholder code
def validate_email(email):
    pass  # ❌ TODO: implement
```

### Cross-Language Leakage
```python
# JavaScript patterns in Python
items.push(x)  # ❌ Should be items.append(x)
if items.length > 0:  # ❌ Should be len(items) > 0

# Java patterns in Python
if text.equals("hello"):  # ❌ Should be text == "hello"
```

## Tips

1. **Start lenient**: Use `--severity high` initially to avoid overwhelming results
2. **Configure ignores**: Add test directories and generated code to ignore patterns
3. **Use in CI**: Catch issues before they reach production
4. **Review regularly**: Run `deeplint .` periodically to maintain code quality
5. **Combine with other tools**: DeepLint complements traditional linters (pylint, eslint)

## When to Use

- ✅ After using AI code generation tools
- ✅ During code review of AI-assisted contributions
- ✅ As part of CI/CD pipeline
- ✅ Before major releases
- ✅ When onboarding AI coding assistants to a project

## When NOT to Use

- ❌ As a replacement for human code review
- ❌ Instead of traditional linters (use both!)
- ❌ For security scanning (use dedicated security tools)
- ❌ For type checking (use mypy/pyright/tsc)

## Learn More

- **GitHub**: https://github.com/del-zhenwu/deeplint
- **Documentation**: See AGENTS.md for development details
- **PyPI**: https://pypi.org/project/deeplint/
