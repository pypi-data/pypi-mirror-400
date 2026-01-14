# Contributing to Neon

Thank you for your interest in contributing to elemental-neon! This document provides guidelines and instructions for contributing.

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/MarsZDF/neon.git
   cd neon
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in development mode**
   ```bash
   pip install -e ".[test]"
   ```

4. **Install pre-commit hooks** (optional but recommended)
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=neon --cov-report=html

# Run specific test file
pytest tests/test_compare.py -v
```

## Code Style

We use:
- **ruff** for linting and formatting
- **mypy** for type checking

```bash
# Check code style
ruff check src/neon tests/

# Format code
ruff format src/neon tests/

# Type check
mypy src/neon --strict
```

## Design Principles

1. **Zero dependencies** - Only use Python standard library
2. **Pure functions** - No state, easy to test
3. **Explicit tolerances** - No magic defaults that silently change behavior
4. **IEEE 754 aware** - Proper handling of NaN, inf, denormals
5. **Fail loudly** - Raise exceptions for invalid inputs
6. **Type hints** - Full type annotations with strict mypy

## Testing Guidelines

- All new functions must have tests
- Aim for 90%+ code coverage
- Test edge cases: NaN, inf, zero, negative zero
- Include docstring examples that can serve as doctests

## Documentation

- Use Google-style docstrings
- Include examples in docstrings
- Update README.md for new features
- Update CHANGELOG.md following [Keep a Changelog](https://keepachangelog.com/)

## Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write tests first (TDD encouraged)
   - Implement your feature
   - Ensure all tests pass
   - Update documentation

3. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: brief description"
   ```

4. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a pull request on GitHub.

5. **PR Requirements**
   - [ ] All tests pass
   - [ ] Code coverage remains ≥90%
   - [ ] Type checking passes (mypy --strict)
   - [ ] Documentation updated
   - [ ] CHANGELOG.md updated

## Versioning

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Incompatible API changes
- **MINOR**: New features, backwards-compatible
- **PATCH**: Bug fixes, backwards-compatible

## Questions?

Open an issue on GitHub or start a discussion.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
