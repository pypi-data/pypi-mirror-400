# Contributing to mm-async-client

Thank you for your interest in contributing to mm-async-client!

## Development Setup

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/mm-async-client.git
cd mm-async-client

# Create virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

# Install with dev dependencies
pip install -e ".[dev]"
```

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/mm_async --cov-report=term-missing

# Run specific test file
pytest tests/test_client.py

# Run tests with specific marker
pytest -m unit
pytest -m "not slow"
```

### Code Quality

```bash
# Lint code
ruff check src/ tests/

# Auto-fix linting issues
ruff check --fix src/ tests/

# Type checking
mypy src/
```

### Pre-commit Hooks

We recommend using pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

## Code Style

- Line length: 79 characters (PEP 8)
- Use type hints for all public functions
- Follow PEP 8 guidelines
- Use Google-style docstrings

### Example

```python
async def get_user(self, user_id: str) -> User:
    """Retrieve a user by their ID.

    Args:
        user_id: The unique identifier of the user.

    Returns:
        User object containing user details.

    Raises:
        MattermostNotFoundError: If user does not exist.
        MattermostValidationError: If user_id is invalid.
    """
    _validate_id(user_id, "user_id")
    data = await self._client.get(f"/users/{user_id}")
    return User.model_validate(data)
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Ensure code passes linting (`ruff check`)
7. Commit your changes using conventional commits
8. Push to your fork
9. Open a Pull Request

### Commit Messages

Use conventional commits:

```
type: subject (imperative, max 72 chars)

- body explains what and why
- wrap at 72 chars
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`

Examples:
- `feat: add pagination support to search methods`
- `fix: handle rate limit headers correctly`
- `docs: update API reference with new methods`

## Reporting Issues

When reporting issues, please include:

1. Python version (`python --version`)
2. Package version (`pip show mm-async`)
3. Mattermost server version (if applicable)
4. Minimal code to reproduce the issue
5. Full error traceback

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
