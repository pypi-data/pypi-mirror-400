# Contributing to mdx_better_lists

Thank you for considering contributing to mdx_better_lists! This document provides guidelines and instructions for contributing.

## How to Contribute

### Pull Requests

1. Fork the repository and create your branch from `main`
2. Follow the [Development Setup](#development-setup) instructions
3. Write tests for your changes (we follow a [test-driven development (TDD)](#test-driven-development-tdd) approach)
4. Ensure all tests pass
5. Use [conventional commits](#commit-messages) for your commits
6. Update documentation as needed
7. Submit your pull request!

## Development Setup

### 1. Clone and Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/mdx_better_lists.git
cd mdx_better_lists

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
pip install -r requirements-dev.txt
```

### 2. Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=mdx_better_lists --cov-report=html

# Run specific test file
pytest tests/test_basic.py

# Run specific test
pytest tests/test_basic.py::TestSimpleUnorderedLists::test_simple_minus_unordered_list
```

### 3. Code Quality

We use black, isort, and flake8 to maintain code quality:

```bash
# Format code
black mdx_better_lists tests

# Sort imports
isort mdx_better_lists tests

# Lint
flake8 mdx_better_lists tests
```

**Important**: All code must pass linting before being merged. The CI pipeline will check this automatically.

## Test-Driven Development (TDD)

This project follows TDD principles. When adding a new feature:

### TDD Workflow

1. **Write a failing test** that describes the desired behavior
2. **Run the test** to confirm it fails
3. **Write minimal code** to make the test pass
4. **Refactor** if needed while keeping tests passing
5. **Repeat** for additional scenarios

### Example

```python
# 1. Write the test first (in tests/test_new_feature.py)
def test_new_config_option(self, md_custom):
    """Test new configuration option."""
    md = md_custom(new_option=True)
    input = """Test markdown"""
    expected = """Expected output"""
    result = convert(md, input)
    assert result == expected

# 2. Run test - it should fail
# pytest tests/test_new_feature.py

# 3. Implement the feature in mdx_better_lists/extension.py

# 4. Run test again - it should pass
# pytest tests/test_new_feature.py

# 5. Run all tests to ensure nothing broke
# pytest tests/
```

## Commit Messages

We use [Conventional Commits](https://www.conventionalcommits.org/) for automatic versioning and changelog generation.

### Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

- **feat**: A new feature (triggers MINOR version bump)
- **fix**: A bug fix (triggers PATCH version bump)
- **docs**: Documentation only changes
- **style**: Code style changes (formatting, missing semicolons, etc.)
- **refactor**: Code refactoring without changing functionality
- **perf**: Performance improvements
- **test**: Adding or updating tests
- **chore**: Build process or auxiliary tool changes

### Breaking Changes

For breaking changes, add `!` after the type or include `BREAKING CHANGE:` in the footer:

```bash
# Using !
git commit -m "feat!: change default value of split_paragraph_lists"

# Using footer
git commit -m "feat: update API

BREAKING CHANGE: removed deprecated preserve_whitespace option"
```

### Examples

```bash
# Feature
git commit -m "feat: add support for nested code blocks in lists"

# Bug fix
git commit -m "fix: handle empty list items correctly"

# Documentation
git commit -m "docs: add example for preserve_numbers config"

# Multiple changes
git commit -m "feat: add new configuration option

- Add split_on_double_newline option
- Update README with usage examples
- Add tests for new behavior"
```
