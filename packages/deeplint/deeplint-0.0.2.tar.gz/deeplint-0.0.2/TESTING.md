# Testing Guide for DeepLint

## Test Coverage Summary

DeepLint has comprehensive test coverage across all supported languages.

### Current Test Statistics

- **Total Tests**: 114 passing
- **Code Coverage**: 83%+
- **Languages Covered**: Python, Go, JavaScript, TypeScript
- **Test Suites**: 8 main test files

## Test Structure

### Language-Specific Tests

#### Python (`test_python_patterns.py`) - 15 tests
Tests for Python-specific AI slop patterns:

- **Noise Patterns**: Redundant comments, empty docstrings
- **Hallucination Patterns**: Wrong imports, JavaScript methods in Python
- **Style Patterns**: Overconfident/hedging comments
- **Structural Patterns**: Single-method classes
- **Placeholder Detection**: `pass`, `...`, `NotImplementedError`
- **Language Filtering**: Python-only file scanning
- **Integration Tests**: Multiple patterns, clean code validation

#### Go (`test_go_patterns.py`) - 7 tests
Tests for Go language support:

- Debug print statements
- Overconfident/hedging comments
- Redundant comments
- TODO comments
- Python patterns leaked into Go code
- Clean Go code validation
- Language filtering

#### JavaScript/TypeScript (`test_js_patterns.py`) - 11 tests
Tests for basic JS/TS patterns:

- Debug console statements
- Overconfident/hedging comments
- Outdated `var` keyword usage
- Commented-out code
- Language filtering (JS vs TS)
- Clean code validation

#### Advanced JS/TS/React (`test_karpeslop_patterns.py`) - 22 tests
Tests for advanced JavaScript/TypeScript/React patterns:

- **Hallucinated Imports**: React/Next.js APIs from wrong packages
- **TypeScript Issues**: `any` type usage, unsafe type assertions
- **React Anti-patterns**: useEffect derived state, setState in loops
- **Style Issues**: Unnecessary IIFE, nested ternary abuse
- **Quality Issues**: TODO placeholders, missing error handling
- **Noise Patterns**: Boilerplate comments, production console logs

### Core Pattern Tests

#### Pattern Detection (`test_patterns/`) - 20 tests

**Hallucinations** (`test_hallucinations.py`):
- Placeholder detection (pass, ellipsis, NotImplementedError)
- Hallucinated imports (wrong modules)
- Cross-language patterns (JS, Java, Ruby, Go, C#, PHP in Python)
- Valid code not flagged

**Structure** (`test_structure.py`):
- Single-method classes
- Multi-method classes (should not flag)

### Integration Tests

#### Corpus Tests (`corpus/test_corpus.py`) - 6 tests

**False Positives** (valid code that should NOT be flagged):
- Abstract methods
- Valid Python methods

**True Positives** (problematic code that SHOULD be flagged):
- JavaScript patterns in Python
- Hallucinated imports
- Placeholder functions
- Java patterns in Python

### Infrastructure Tests

#### Language Detection (`test_language_detector.py`) - 12 tests
- Extension to language mapping
- Language parsing from CLI arguments
- Multi-language detection in directories
- Edge cases (empty directories, no supported files)

#### CLI Multi-language (`test_cli_multi_language.py`) - 12 tests
- Automatic language detection
- Manual language override
- Language filtering
- JSON output with language info
- Case-insensitive language names

#### Configuration (`test_config.py`) - 8 tests
- Config defaults
- Loading from pyproject.toml
- CLI argument merging
- Config file discovery

## Running Tests

### Quick Start

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/deeplint --cov-report=term-missing

# Run specific test file
pytest tests/test_python_patterns.py -v
```

### Language-Specific Testing

```bash
# Test Python patterns
pytest tests/test_python_patterns.py -v

# Test Go patterns
pytest tests/test_go_patterns.py -v

# Test JavaScript/TypeScript patterns
pytest tests/test_js_patterns.py -v
pytest tests/test_karpeslop_patterns.py -v

# Test language detection
pytest tests/test_language_detector.py -v
```

### Testing Specific Pattern Categories

```bash
# Test hallucination detection
pytest tests/test_patterns/test_hallucinations.py -v

# Test structural patterns
pytest tests/test_patterns/test_structure.py -v

# Test corpus (integration tests)
pytest tests/corpus/test_corpus.py -v
```

## CI/CD Testing

### GitHub Actions Workflows

#### CI Workflow (`.github/workflows/ci.yml`)
Runs on every push and pull request to `main`:

1. **Test Job**: 
   - Matrix testing on Python 3.9, 3.10, 3.11, 3.12
   - Runs all 114 tests
   - Generates coverage report
   - Uploads to Codecov

2. **Lint Job**:
   - Ruff format checking
   - Black and isort checks
   - Type checking with mypy

3. **Security Job**:
   - pip-audit dependency scanning

4. **Self-Check Job**:
   - Runs DeepLint on itself
   - Ensures dogfooding

#### Publish Workflow (`.github/workflows/publish.yml`)
Triggered on GitHub releases:

1. **Build Job**:
   - Builds source distribution and wheel
   - Uploads artifacts

2. **Publish Job**:
   - Downloads build artifacts
   - Publishes to PyPI using trusted publishing

## Test Fixtures

### Directory Structure

```
tests/
├── fixtures/
│   ├── go/              # Go test files
│   │   ├── sample_with_issues.go
│   │   └── clean_code.go
│   └── js/              # JavaScript/TypeScript test files
│       ├── sample_with_issues.js
│       ├── sample_with_issues.ts
│       ├── karpeslop_patterns.ts
│       ├── clean_code.js
│       └── clean_react.tsx
└── corpus/
    ├── true_positives/   # Code that should trigger warnings
    │   ├── hallucinated_imports.py
    │   ├── java_patterns.py
    │   ├── js_patterns.py
    │   ├── mutable_defaults.py
    │   └── placeholder_functions.py
    └── false_positives/  # Valid code that shouldn't trigger warnings
        ├── abstract_methods.py
        ├── valid_python_methods.py
        ├── local_imports.py
        ├── well_known_constants.py
        └── multiline_strings.py
```

## Coverage Goals

Current coverage by module:

| Module | Coverage | Notes |
|--------|----------|-------|
| `language_detector.py` | 100% | Fully covered |
| `patterns/go/` | 100% | All Go patterns covered |
| `patterns/js/` | 100% | All JS/TS patterns covered |
| `patterns/noise.py` | 100% | Noise patterns covered |
| `patterns/style.py` | 100% | Style patterns covered |
| `patterns/base.py` | 96% | Core pattern infrastructure |
| `cli.py` | 92% | CLI interface |
| `detector.py` | 83% | Main detection logic |
| `config.py` | 84% | Configuration handling |
| `analyzer/ast_analyzer.py` | 84% | AST analysis |
| Overall | 83% | Good coverage across all modules |

## Adding New Tests

When adding new patterns or features:

1. **Create focused tests** for the specific pattern
2. **Test both detection and non-detection** (positive and negative cases)
3. **Add test fixtures** for complex scenarios
4. **Update test counts** in README and TESTING.md
5. **Ensure all tests pass** before submitting PR

### Example Test Structure

```python
def test_new_pattern_detected(tmp_python_file):
    """Test that the new pattern is detected."""
    code = """
    # Code that should trigger the pattern
    def bad_code():
        problematic_pattern()
    """
    file = tmp_python_file(code)
    detector = Detector(languages=["python"])
    issues = detector.scan([file])
    
    pattern_issues = [i for i in issues if i.pattern_id == "new_pattern"]
    assert len(pattern_issues) >= 1, f"Expected new pattern detection"

def test_new_pattern_not_flagged(tmp_python_file):
    """Test that valid code doesn't trigger the pattern."""
    code = """
    # Valid code that should NOT trigger the pattern
    def good_code():
        correct_approach()
    """
    file = tmp_python_file(code)
    detector = Detector(languages=["python"])
    issues = detector.scan([file])
    
    pattern_issues = [i for i in issues if i.pattern_id == "new_pattern"]
    assert len(pattern_issues) == 0, f"Valid code should not trigger pattern"
```

## Test Quality Standards

All tests should:

1. ✅ Have clear, descriptive names
2. ✅ Test one specific behavior
3. ✅ Include both positive and negative cases
4. ✅ Use appropriate fixtures
5. ✅ Have meaningful assertion messages
6. ✅ Be independent (no test interdependencies)
7. ✅ Run quickly (< 1 second per test)

## Continuous Improvement

We're continuously working to improve test coverage:

- [ ] Add more edge case tests
- [ ] Increase coverage of error handling paths
- [ ] Add performance benchmarks
- [ ] Add integration tests for multi-file analysis
- [ ] Add tests for configuration edge cases

## Questions?

See:
- [README.md](README.md) - Main documentation
- [AGENTS.md](AGENTS.md) - Pattern implementation guide
- [GitHub Actions](https://github.com/del-zhenwu/deeplint/actions) - CI/CD status
