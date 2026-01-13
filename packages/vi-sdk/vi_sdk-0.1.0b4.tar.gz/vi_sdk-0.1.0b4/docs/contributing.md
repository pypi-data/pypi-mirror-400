# Contributing to Vi SDK

Thank you for your interest in contributing to the Datature Vi SDK! This guide will help you get started.

## Code of Conduct

Please read and follow our [Code of Conduct](https://github.com/datature/Vi-SDK/blob/main/pypi/vi-sdk/CODE_OF_CONDUCT.md) to keep our community approachable and respectable.

## Ways to Contribute

### Reporting Bugs

Found a bug? Please create an issue with:

- **Clear title** describing the problem
- **Steps to reproduce** the issue
- **Expected behavior** vs actual behavior
- **Environment details** (OS, Python version, SDK version)
- **Code snippet** demonstrating the issue
- **Error messages** and stack traces

### Suggesting Features

Have an idea? Open an issue with:

- **Clear description** of the feature
- **Use cases** explaining why it's needed
- **Examples** of how it would be used
- **Alternatives** you've considered

### Improving Documentation

Documentation improvements are always welcome:

- Fix typos or unclear explanations
- Add examples or clarify existing ones
- Improve API documentation
- Add guides for common workflows

### Contributing Code

Ready to contribute code? Great! Follow the guidelines below.

## Development Setup

### Prerequisites

- Python 3.10 or higher
- `uv` package manager (recommended) or `pip`
- Git

### Initial Setup

1. **Fork the repository** on GitHub

2. **Clone your fork:**

   ```bash
   git clone https://github.com/YOUR-USERNAME/Vi-SDK.git
   cd Vi-SDK/pypi/vi-sdk
   ```

3. **Install dependencies:**

   ```bash
   # With uv (recommended)
   uv sync

   # Or with pip
   python3 -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -e ".[dev]"
   ```

4. **Create a branch:**

   ```bash
   git checkout -b feature/your-feature-name
   ```

## Coding Standards

### Style Guide

We follow PEP 8 with some modifications enforced by Ruff:

- **Line length**: 88 characters (Black default)
- **Quotes**: Double quotes for strings
- **Imports**: Sorted and grouped
- **Type hints**: Required for all functions
- **Docstrings**: Google-style format

### Linting

Run linters before committing:

```bash
# Format code
ruff format .

# Check for issues
ruff check .

# Fix auto-fixable issues
ruff check --fix .
```

### Type Checking

We use Python 3.10+ type hints:

```python
from typing import Any

def fetch_data(url: str, timeout: int = 30) -> dict[str, Any]:
    """Fetch data from URL.

    Args:
        url: The URL to fetch from
        timeout: Request timeout in seconds

    Returns:
        Dictionary containing the response data

    Raises:
        ValueError: If URL is invalid
        TimeoutError: If request times out
    """
    ...
```

### Docstring Format

Use Google-style docstrings:

```python
def example_function(param1: str, param2: int = 10) -> bool:
    """Short one-line description.

    More detailed description explaining the function's purpose,
    behavior, and any important notes.

    Args:
        param1: Description of param1
        param2: Description of param2. Defaults to 10.

    Returns:
        Description of return value

    Raises:
        ErrorType: When this error occurs

    Examples:
        >>> result = example_function("value", 20)
        >>> print(result)
        True

    Note:
        Additional notes if needed

    See Also:
        - Related function or class
    """
    ...
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_client.py

# Run with coverage
pytest --cov=vi --cov-report=html

# Run integration tests (requires API credentials)
export DATATURE_VI_SECRET_KEY="your-secret-key"
export DATATURE_VI_ORGANIZATION_ID="your-organization-id"
pytest tests/integrations/
```

### Writing Tests

#### Unit Tests

```python
# tests/unit/test_mymodule.py
import pytest
from vi.mymodule import my_function

def test_my_function_success():
    """Test successful execution."""
    result = my_function("input")
    assert result == "expected_output"

def test_my_function_error():
    """Test error handling."""
    with pytest.raises(ValueError, match="Invalid input"):
        my_function("invalid")
```

#### Integration Tests

```python
# tests/integrations/test_mymodule_integration.py
import pytest
from vi import Client

@pytest.fixture
def client():
    """Create client for testing."""
    return Client()

def test_real_api_call(client):
    """Test against real API."""
    result = client.datasets.list()
    assert result.items is not None
```

### Test Coverage

Maintain test coverage above 80%:

```bash
# Generate coverage report
pytest --cov=vi --cov-report=term --cov-report=html

# View HTML report
open htmlcov/index.html
```

## Pull Request Process

### Before Submitting

1. **Run tests:** Ensure all tests pass
2. **Run linters:** Fix all linting issues
3. **Update documentation:** Add docstrings and update guides
4. **Add tests:** Cover new functionality
5. **Update CHANGELOG:** Document your changes

### PR Guidelines

1. **Title:** Clear, descriptive title
   - ✅ Good: "Add retry logic to dataset download"
   - ❌ Bad: "Fix bug"

2. **Description:** Include:
   - What changed and why
   - Related issues (e.g., "Fixes #123")
   - Breaking changes (if any)
   - Testing performed

3. **Commits:**
   - Use clear commit messages
   - Keep commits atomic and focused
   - Squash fixup commits before merging

4. **Code Review:**
   - Respond to feedback promptly
   - Make requested changes
   - Resolve merge conflicts

### PR Template

```markdown
## Description

Brief description of changes

## Related Issues

Fixes #(issue number)

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing

- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All tests passing
- [ ] Manual testing performed

## Checklist

- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] Tests added for changes
- [ ] All tests passing
```

## Project Structure

```
vi-sdk/
├── vi/
│   ├── __init__.py          # Public API exports
│   ├── api/                 # High-level API client
│   │   ├── client.py        # Main client
│   │   ├── pagination.py    # Pagination utilities
│   │   └── resources/       # Resource endpoints
│   ├── client/              # Low-level HTTP client
│   │   ├── auth.py          # Authentication
│   │   ├── http/            # HTTP layer
│   │   └── errors/          # Error classes
│   ├── dataset/             # Dataset loaders
│   │   └── loaders/         # Data loading utilities
│   ├── inference/           # Inference utilities
│   │   ├── loaders/         # Model loaders
│   │   └── predictors/      # Prediction classes
│   ├── logging/             # Logging configuration
│   └── utils/               # Shared utilities
├── tests/
│   ├── unit/                # Unit tests
│   └── integrations/        # Integration tests
├── docs/                    # Documentation
├── examples/                # Example scripts
└── pyproject.toml           # Project configuration
```

## Adding New Features

### 1. API Endpoints

To add a new API endpoint:

1. Create types in `vi/api/resources/{resource}/types.py`
2. Create responses in `vi/api/resources/{resource}/responses.py`
3. Add methods to resource class in `vi/api/resources/{resource}/{resource}.py`
4. Add tests in `tests/unit/test_{resource}.py`
5. Add integration tests in `tests/integrations/test_{resource}_integration.py`
6. Document in `docs/api/resources/{resource}.md`

### 2. Error Types

To add a new error type:

1. Add class in `vi/client/errors/errors.py`:

   ```python
   class ViMyError(ViError):
       """My custom error."""
       pass
   ```

2. Export in `vi/client/errors/__init__.py`
3. Add tests in `tests/unit/test_errors.py`
4. Document in `docs/api/errors.md`

### 3. Dataset Loaders

To add a new loader:

1. Create loader in `vi/dataset/loaders/`
2. Add types in `vi/dataset/loaders/types/`
3. Add tests
4. Document in `docs/api/dataset-loaders.md`

## Documentation

### Building Documentation

```bash
cd pypi/vi-sdk

# Install dependencies
pip install -r docs-requirements.txt

# Serve locally
mkdocs serve

# Build static site
mkdocs build

# Deploy to GitHub Pages
mkdocs gh-deploy
```

### Documentation Guidelines

- Use clear, concise language
- Provide code examples
- Include real-world use cases
- Link to related documentation
- Keep examples up to date

## Release Process

### Versioning

We follow [Semantic Versioning](https://semver.org/):

- **Major** (X.0.0): Breaking changes
- **Minor** (x.X.0): New features (backward compatible)
- **Patch** (x.x.X): Bug fixes

### Release Checklist

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Run full test suite
4. Build package: `python -m build`
5. Test package in clean environment
6. Create GitHub release
7. Publish to PyPI

## Getting Help

- **Questions:** Open a discussion on GitHub
- **Bugs:** Create an issue
- **Security:** Email developers@datature.io
- **Chat:** Join our community (link in README)

## Recognition

Contributors will be:

- Listed in `CONTRIBUTORS.md`
- Mentioned in release notes
- Credited in documentation (for significant contributions)

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.

---

Thank you for contributing to Vi SDK! 🎉
