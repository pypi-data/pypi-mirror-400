# Contributing to Qualpal

Thank you for your interest in contributing to qualpal-py! This document
provides guidelines and instructions for contributing.

## Overview

Qualpal-py is a Python package that provides bindings to the [qualpal C++
library](https://github.com/jolars/qualpal). The architecture consists of:

- **Python layer** (`qualpal/`): API, data structures, validation,
  visualization, and display
- **C++ layer** (`src/`): Bindings to the qualpal C++ library for
  performance-critical algorithms

## Where to Contribute

### Python Package Contributions

Contributions to the Python package (this repository) are welcome for:

- **New features** in the Python API (data structures, utilities,
  visualization)
- **Bug fixes** in Python code or C++ bindings
- **Documentation** improvements
- **Tests** and test coverage
- **Examples** and tutorials

### Core Algorithm Contributions

If you want to contribute to the **core color palette algorithms**, please
contribute directly to the [qualpal C++
library](https://github.com/jolars/qualpal) instead. The Python package uses
that library as a dependency.

## Development Setup

### Prerequisites

- A stable Python installation
- C++17 compatible compiler (GCC, Clang, or MSVC)
- [uv](https://github.com/astral-sh/uv) package manager (recommended)

### Installation

```bash
# Clone the repository
git clone https://github.com/jolars/qualpal-py.git
cd qualpal-py

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install development dependencies
uv pip install -e . --group dev

# Or with visualization support
uv pip install -e .[viz] --group dev
```

## Development Workflow

### Before Making Changes

1. **Check existing issues** to see if your idea is already being discussed
2. **Open an issue** to discuss major changes before implementing
3. **Create a branch** from `main` for your changes

### Making Changes

1. **Make minimal, focused changes** - one feature or fix per pull request
2. **Follow the existing code style** (automatically enforced by ruff)
3. **Add tests** for new features or bug fixes
4. **Update documentation** if changing public APIs

### Code Quality Requirements

All code must pass these checks before merging:

```bash
# 1. Format code (automatically fixes issues)
ruff format .

# 2. Fix linting issues (automatically fixes most issues)
ruff check --fix .

# 3. Type check (requires manual fixes)
basedpyright qualpal

# 4. Run tests
python -m pytest
```

**Pre-commit hooks** will automatically run `ruff format` and `ruff check` on commit.

### Verification Checklist

Before submitting a PR, verify all checks pass:

```bash
# Verify formatting
ruff format --check .

# Verify linting
ruff check .

# Verify type checking
basedpyright qualpal

# Verify all tests pass
python -m pytest

# Check test coverage (aim for >90%)
python -m coverage run -m pytest
python -m coverage report --include="qualpal/*"
```

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_color.py

# Run tests matching a pattern
python -m pytest -k cvd

# Run with verbose output
python -m pytest -v
```

### Writing Tests

- Place tests in `tests/` directory
- Use descriptive test names: `test_<feature>_<scenario>`
- Follow existing test structure (classes for grouping related tests)
- Use pytest fixtures for common setup
- Add docstrings explaining what each test verifies

Example:

```python
def test_palette_export_css_with_prefix():
    """Test that CSS export includes custom prefix."""
    palette = Palette(["#ff0000", "#00ff00"])
    css = palette.to_css(prefix="custom")
    assert any("--custom-1:" in line for line in css)
```

## Code Style

### Python Code

- **Formatting**: Handled automatically by `ruff format`
- **Linting**: Enforced by `ruff check`
- **Docstrings**: NumPy style (enforced by ruff)
- **Type hints**: Required for public APIs, checked by basedpyright
- **Imports**: Sorted automatically by ruff

Example docstring:

```python
def example_function(name: str, count: int = 5) -> list[str]:
    """Short one-line summary.

    Longer description if needed, explaining the function's purpose
    and behavior in more detail.

    Parameters
    ----------
    name : str
        Description of name parameter.
    count : int, default=5
        Description of count parameter.

    Returns
    -------
    list[str]
        Description of return value.

    Examples
    --------
    >>> example_function("test", 3)
    ['test', 'test', 'test']
    """
    return [name] * count
```

### C++ Code

- **Standard**: C++17
- **Style**: Follow existing code conventions
- **Comments**: Use Doxygen-style comments for public functions
- **Headers**: Include guards with `#pragma once`

## Pull Request Process

1. **Update your branch** with the latest `main` before submitting
2. **Run all checks** and ensure they pass
3. **Write a clear PR description** explaining:
   - What changes you made
   - Why you made them
   - How to test them
4. **Link related issues** using "Fixes #123" or "Closes #456"
5. **Keep PRs focused** - one feature or fix per PR
6. **Respond to feedback** and make requested changes

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/) format:

```
type(scope): brief description

Longer description if needed.

Fixes #123
```

Types:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `chore`: Maintenance tasks

Examples:

- `feat: add get_palette function`
- `fix: correct CVD simulation for deuteranopia`
- `docs: update installation instructions`

## Documentation

### Building Documentation

```bash
cd docs
make html
```

Output will be in `docs/build/html/index.html`.

### Documentation Structure

- **Tutorial** (`docs/source/tutorial.md`): Comprehensive user guide
- **API Reference** (`docs/source/api.md`): Auto-generated from docstrings
- **Changelog** (`docs/source/changelog.md`): Version history

When adding new features:

1. Add docstrings to all public functions/classes
2. Consider adding examples to the tutorial
3. Update API reference if needed

## Questions?

- **Issues**: Open an issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Email**: Contact the maintainer via the email in `pyproject.toml`

## License

By contributing, you agree that your contributions will be licensed under the
same [MIT License](LICENSE) that covers this project.
