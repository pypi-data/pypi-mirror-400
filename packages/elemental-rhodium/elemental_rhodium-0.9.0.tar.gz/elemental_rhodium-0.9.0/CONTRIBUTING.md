# Contributing to Rhodium

Thank you for your interest in contributing to Rhodium! We welcome contributions from everyone.

## Getting Started

1.  **Fork the repository** on GitHub.
2.  **Clone your fork** locally:
    ```bash
    git clone https://github.com/your-username/rhodium.git
    cd rhodium
    ```
3.  **Set up a virtual environment** and install dependencies:
    ```bash
    python -m venv venv
    source venv/bin/activate  # or venv\Scripts\activate on Windows
    pip install -e ".[test]"
    ```

## Development Workflow

### Running Tests

We use `pytest` for testing. Run the full test suite with:

```bash
pytest
```

To run a specific test file:

```bash
pytest tests/test_bbox.py
```

### Code Style & Linting

We use `ruff` for linting and formatting, and `mypy` for static type checking.

1.  **Linting & Formatting:**
    ```bash
    pip install ruff
    ruff check .
    ruff format .
    ```

2.  **Type Checking:**
    ```bash
    pip install mypy
    mypy rhodium
    ```

Please ensure all checks pass before submitting your Pull Request.

## Submitting a Pull Request

1.  Create a new branch for your feature or bugfix:
    ```bash
    git checkout -b feature/my-new-feature
    ```
2.  Make your changes and add tests if applicable.
3.  Ensure all tests and linting checks pass.
4.  Commit your changes with clear, descriptive messages.
5.  Push your branch to your fork:
    ```bash
    git push origin feature/my-new-feature
    ```
6.  Open a Pull Request against the `main` branch of the original repository.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
