# Tests

This directory contains unit tests for the Time to Shop application.

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/time_to_shop --cov-report=html

# Run specific test file
pytest tests/test_config.py

# Run with verbose output
pytest -v
```

## Test Structure

- `test_config.py`: Tests for configuration management
- `test_constants.py`: Tests for application constants
- `conftest.py`: Pytest fixtures and shared test utilities

## Writing Tests

When adding new tests:
1. Follow the naming convention `test_*.py`
2. Use descriptive test function names starting with `test_`
3. Group related tests in classes (optional)
4. Use fixtures from `conftest.py` for common test data
5. Aim for high code coverage (>80%)

## Test Coverage

View coverage report after running tests with `--cov`:
- Terminal: Shows coverage percentage per file
- HTML: Open `htmlcov/index.html` in browser for detailed report
