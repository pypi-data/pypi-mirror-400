# Contributing to weathervault

Thank you for your interest in contributing to weathervault!

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/rich-iannone/weathervault.git
cd weathervault
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

3. Run tests:
```bash
make test
# Or directly:
pytest
```

## Running Tests

We use pytest for testing. Run the full test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=weathervault

# Run specific test file
pytest tests/test_stations.py

# Run tests without network access (skip network-dependent tests)
pytest -m "not network"
```

## Code Style

We use [ruff](https://github.com/astral-sh/ruff) for linting and formatting:

```bash
# Check code style
ruff check .

# Auto-fix issues
ruff check --fix .

# Format code
ruff format .
```

## Making Changes

1. Create a new branch for your feature or bugfix
2. Make your changes
3. Add tests for new functionality
4. Ensure all tests pass
5. Update documentation as needed
6. Submit a pull request

## Release Process

Releases are automated via GitHub Actions when a new release is created. The workflow will:

1. Run all tests across multiple platforms and Python versions
2. Build the package
3. Publish to PyPI

## Questions?

Feel free to open an issue for questions or discussions!
