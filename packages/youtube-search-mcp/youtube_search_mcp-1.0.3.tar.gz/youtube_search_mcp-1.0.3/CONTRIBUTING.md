# Contributing to YouTube Search MCP

First off, thank you for considering contributing! It's people like you that make open source such a great community. We welcome any form of contribution, from reporting bugs and suggesting enhancements to submitting pull requests.

## Ways to Contribute

-   **[Report a Bug](https://github.com/JIHAK-dev/youtube-search-mcp/issues/new?template=bug_report.md)**: If you find a bug, please let us know!
-   **[Suggest an Enhancement](https://github.com/JIHAK-dev/youtube-search-mcp/issues/new?template=feature_request.md)**: Have an idea to make this project better? We'd love to hear it.
-   **Submit a Pull Request**: If you want to contribute code, please follow the process below.

## Pull Request Process

1.  **Fork the Repository**: Click the 'Fork' button at the top right of this page.
2.  **Clone Your Fork**:
    ```bash
    git clone https://github.com/YourUsername/youtube-search-mcp.git
    cd youtube-search-mcp
    ```
3.  **Create a Branch**:
    Create a new branch for your feature or bug fix.
    ```bash
    git checkout -b feature/AmazingFeature
    # or
    git checkout -b fix/SomeBug
    ```
4.  **Set Up Your Environment**:
    Follow the [developer setup instructions in the README](https://github.com/JIHAK-dev/youtube-search-mcp#%EF%B8%8F-for-developers--contributors) to install dependencies.
5.  **Make Your Changes**:
    Write your code. Ensure it follows the existing code style.
6.  **Run Quality Checks**:
    Before committing, make sure all checks pass:
    ```bash
    uv run black .
    uv run ruff check .
    uv run mypy .
    uv run pytest
    ```
7.  **Commit Your Changes**:
    Use a clear and descriptive commit message.
    ```bash
    git commit -m "feat: Add some AmazingFeature"
    ```
8.  **Push to Your Branch**:
    ```bash
    git push origin feature/AmazingFeature
    ```
9.  **Open a Pull Request**:
    Go to the original repository and open a pull request. Provide a clear description of the problem and solution. Include the relevant issue number if applicable.

## Code of Conduct

This project and everyone participating in it are governed by our [Code of Conduct](https://github.com/JIHAK-dev/youtube-search-mcp/blob/main/CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior.

Thank you for your contribution!
