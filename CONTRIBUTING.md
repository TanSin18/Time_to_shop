# Contributing to Time to Shop

Thank you for your interest in contributing to Time to Shop! This document provides guidelines and instructions for contributing.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
   ```bash
   git clone https://github.com/YOUR_USERNAME/Time_to_shop.git
   cd Time_to_shop
   ```
3. **Set up development environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```
4. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

## Development Workflow

1. **Create a branch** for your changes
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our coding standards

3. **Write tests** for your changes
   ```bash
   pytest tests/test_your_module.py
   ```

4. **Run code quality checks**
   ```bash
   # Format code
   black src/ tests/
   isort src/ tests/

   # Lint code
   flake8 src/ tests/
   pylint src/time_to_shop

   # Type checking
   mypy src/time_to_shop

   # Run all tests
   pytest --cov
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Brief description of changes"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request** on GitHub

## Coding Standards

### Python Style
- Follow PEP 8 guidelines
- Use Black for code formatting (line length: 100)
- Use isort for import sorting
- Maximum line length: 100 characters

### Documentation
- Add docstrings to all functions, classes, and modules
- Use Google-style docstrings
- Update README if adding new features

### Type Hints
- Use type hints for all function parameters and return values
- Use `Optional[Type]` for optional parameters
- Import types from `typing` module

### Example

```python
from typing import Optional, List
import pandas as pd


def process_data(
    data: pd.DataFrame,
    columns: Optional[List[str]] = None
) -> pd.DataFrame:
    """Process input data with optional column filtering.

    Args:
        data: Input DataFrame to process.
        columns: Optional list of columns to keep. If None, keeps all.

    Returns:
        Processed DataFrame.

    Raises:
        ValueError: If columns don't exist in data.
    """
    if columns and not all(col in data.columns for col in columns):
        raise ValueError("Some columns not found in data")

    result = data[columns] if columns else data
    return result
```

## Testing Guidelines

### Writing Tests
- Write tests for all new functionality
- Aim for >80% code coverage
- Use pytest fixtures for common test data
- Test edge cases and error conditions

### Test Structure
```python
import pytest
from your_module import YourClass


class TestYourClass:
    """Tests for YourClass."""

    def test_basic_functionality(self):
        """Test basic functionality works as expected."""
        obj = YourClass()
        result = obj.method()
        assert result == expected_value

    def test_error_handling(self):
        """Test error handling for invalid input."""
        obj = YourClass()
        with pytest.raises(ValueError):
            obj.method(invalid_input)
```

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_module.py

# Run with coverage
pytest --cov=src/time_to_shop --cov-report=html

# Run with verbose output
pytest -v
```

## Commit Message Guidelines

### Format
```
type(scope): brief description

Detailed explanation of what changed and why.

Fixes #issue_number
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples
```
feat(predictor): add support for custom probability thresholds

Added ability to specify custom probability thresholds for decile
assignment instead of using hardcoded bins.

Fixes #42
```

```
fix(data_loader): handle missing demographic columns gracefully

Previously crashed if demographic columns were missing. Now fills
with default values and logs a warning.

Fixes #38
```

## Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new functionality
3. **Ensure all tests pass** locally
4. **Update CHANGELOG** if applicable
5. **Fill out PR template** with:
   - Description of changes
   - Related issues
   - Testing performed
   - Breaking changes (if any)

### PR Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code formatted with Black
- [ ] All tests pass
- [ ] No linting errors
- [ ] Type hints added
- [ ] Changelog updated (if needed)

## Code Review Process

- All PRs require at least one review
- Address all review comments
- Maintain a respectful, constructive tone
- Be open to feedback and suggestions

## Reporting Issues

### Bug Reports
Include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Error messages/logs
- Sample data (if applicable)

### Feature Requests
Include:
- Clear description of the feature
- Use case and motivation
- Proposed implementation (optional)
- Potential impact on existing functionality

## Questions?

If you have questions about contributing:
- Open a GitHub issue with the `question` label
- Check existing issues and documentation first

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
