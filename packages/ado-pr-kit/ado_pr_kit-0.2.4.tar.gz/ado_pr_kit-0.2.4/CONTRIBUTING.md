# Contributing to AdoPRKit

Thank you for your interest in contributing to AdoPRKit! We welcome contributions from the community to help make this project better.

## How to Contribute

1.  **Fork the repository**: Click the "Fork" button on the top right of the repository page.
2.  **Clone your fork**:
    ```bash
    git clone https://github.com/your-username/AdoPRKit.git
    cd AdoPRKit
    ```
3.  **Set up the development environment**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -e .[dev]
    ```
4.  **Create a new branch**:
    ```bash
    git checkout -b feature/my-new-feature
    ```
5.  **Make your changes**: Implement your feature or fix the bug.
6.  **Run tests**: Ensure all tests pass.
    ```bash
    pytest
    ```
7.  **Commit your changes**: Use clear and descriptive commit messages.
8.  **Push to your fork**:
    ```bash
    git push origin feature/my-new-feature
    ```
9.  **Submit a Pull Request**: Go to the original repository and create a Pull Request from your forked branch.

## Code Style

- We use `black` for code formatting.
- We use `flake8` for linting.
- we use `pre-commit` hooks to ensure code quality.

Please ensure your code adheres to these standards before submitting a PR.

## Reporting Issues

If you find a bug or have a feature request, please open an issue on the GitHub repository. Provide as much detail as possible to help us understand and resolve the issue.
