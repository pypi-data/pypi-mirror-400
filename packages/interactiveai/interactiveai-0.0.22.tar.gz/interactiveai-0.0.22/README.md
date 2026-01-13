# InteractiveAI SDK

The official Python SDK for the InteractiveAI platform. This repository contains the source code for the `interactiveai` package, which is a powerful tool for developing, evaluating, and monitoring AI applications.

## Development and Release Cycle

This project uses `make` to streamline common development and release tasks.

| Command         | Description                                        | Use Case                                                                              |
| --------------- | -------------------------------------------------- | ------------------------------------------------------------------------------------- |
| `make clean`    | Remove previous build artifacts.                   | Use before a new build to ensure a clean state.                                       |
| `make build`    | Build the package for distribution.                | Creates the distributable files in the `dist/` directory.                             |
| `make publish`  | Upload the package to PyPI.                        | Publishes a new version of the package. Requires `twine` to be installed.             |
| `make release`  | Run the full clean, build, and publish cycle.      | A convenient shortcut for releasing a new version.                                    |

---

## Changelog Summary

This is a summary of the most recent changes. For a full history, please see `CHANGELOG.md`.

### Current Features
- **Interactive Class**: The main entry point for the SDK, extending Langfuse functionality with InteractiveAI-specific features.
  - Inherits all Langfuse capabilities (tracing, datasets, prompts, scores, etc.)
  - **`fetch_routines()`**: Asynchronously fetches routines (prompts) from InteractiveAI, filtering by folder and label. Returns a list of routine dictionaries containing name, description, when_it_is_used, and the routine prompt content.

---

## Repository Architecture

The repository is structured to separate the core SDK logic from the application-level code and tests.

```
.
├── src/
│   └── interactiveai/
│       ├── __init__.py
│       └── interactive.py
├── tests/
├── Makefile
├── pyproject.toml
├── README.md
└── README_pypi.md
```

### Component Descriptions

-   **`src/interactiveai/`**: This is the main source directory for the `interactiveai` package.
    -   **`interactive.py`**: The core of the SDK. It contains the `Interactive` class, which extends the Langfuse client and provides InteractiveAI-specific functionality. This class is the primary entry point for users and provides a high-level API for interacting with the InteractiveAI platform.
    -   **`__init__.py`**: Package initialization file that exports the `Interactive` class.

-   **`tests/`**: Contains all the tests for the `interactiveai` package. This directory is not included in the final distribution.

-   **`Makefile`**: A helper file with commands to simplify the development and release process.

-   **`pyproject.toml`**: The main configuration file for the project. It defines the project's metadata, dependencies, and build configuration.

-   **`README.md`**: This file. It is the main README for the GitHub repository.

-   **`README_pypi.md`**: The README file that is displayed on the PyPI package page.

### Dependencies

The SDK depends on:
- **`langfuse~=3.5.2`**: Core Langfuse SDK for tracing, datasets, and prompt management
- **`langchain-core>=0.3.68`**: LangChain core functionality
- **`loguru>=0.7.0`**: Logging library

The `Interactive` class extends `Langfuse`, so all Langfuse functionality is available through the `Interactive` instance.

## Usage Example

```python
import asyncio
from interactiveai import Interactive

# Initialize the client
interactive = Interactive(
    public_key="pk-lf-your-public-key",
    secret_key="sk-lf-your-secret-key",
    host="https://app.interactive.ai"
)

# Fetch routines asynchronously
async def main():
    routines = await interactive.fetch_routines(
        routines_folder="routines",
        label="production"
    )
    print(f"Found {len(routines)} routines")
    for routine in routines:
        print(f"- {routine['name']}: {routine['description']}")

# Run the async function
asyncio.run(main())

# All Langfuse methods are also available
# For example: interactive.score(), interactive.trace(), etc.
```

---

## Publishing Checklist

This checklist outlines the steps required to publish a new version of the `interactiveai` package to the Python Package Index (PyPI).

### 📋 Pre-Publishing Checklist

- [ ] **Run Tests**: Ensure all tests pass and the package is stable.
- [ ] **Update Version Number**: Increment the `version` number in your `pyproject.toml` file. PyPI does not allow overwriting an existing version. For example, change `version = "0.0.1"` to `version = "0.0.2"`.
- [ ] **Update Changelog**: (Optional but recommended) Document the new changes in a `CHANGELOG.md` file (**or ask cursor to do it after each task, there are defined cursor rules for that**).
- [ ] **Commit Changes**: Commit all your changes to Git.

### 🚀 Publishing Commands

Once you have completed the checklist, you can use the `make` commands to streamline the process:

1.  **`make build`**: Builds the package and creates the distribution files.
2.  **`make publish`**: Uploads the package to PyPI.
3.  **`make release`**: Runs the full clean, build, and publish cycle.
