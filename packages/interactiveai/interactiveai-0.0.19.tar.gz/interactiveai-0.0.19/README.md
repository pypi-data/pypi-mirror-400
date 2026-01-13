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

### Added
- **Secrets Management Client**:
  - **Rationale**: To enable programmatic access to secrets stored within an InteractiveAI project, which is essential for CI/CD pipelines and automated workflows.
  - **New Clients**:
    - `packages/langfuse/api/resources/secrets/client.py`: Introduced `SecretsClient` and `AsyncSecretsClient` to provide synchronous and asynchronous access to the secrets API. These are exposed via `interactive.api.secrets`.
  - **Methods**:
    - `get(name: str) -> str`: Retrieves the value of a single secret by its name.
- **Evaluator**: Added `Evaluator` class for model-graded evaluations.
- **Interactive Class**: Added `Interactive` class as the main entry point for the SDK, providing methods for dataset management, experiment execution, and prompt/secret retrieval.

---

## Repository Architecture

The repository is structured to separate the core SDK logic from the application-level code and tests.

```
.
├── src/
│   └── interactiveai/
│       ├── evaluators/
│       │   └── evaluators.py
│       └── interactive.py
├── packages/
│   └── langfuse/
│       ├── api/
│       │   └── resources/
│       ├── _client/
│       └── langchain/
├── tests/
├── Makefile
├── pyproject.toml
├── README.md
└── README_pypi.md
```

### Component Descriptions

-   **`src/interactiveai/`**: This is the main source directory for the `interactiveai` package.
    -   **`interactive.py`**: The core of the SDK. It contains the `Interactive` class, which is the primary entry point for users. This class provides a high-level API for interacting with the InteractiveAI platform.
    -   **`evaluators/`**: Contains the `Evaluator` class, which is used for model-graded evaluations.

-   **`packages/langfuse/`**: This directory contains the low-level client for the Langfuse API. The InteractiveAI SDK is built on top of the Langfuse SDK, and this directory contains a fork of it (**forked version : 3.1.3**).
    -   **`api/`**: Contains the auto-generated API client for the Langfuse REST API. This is where all the API resources and data models are defined.
    -   **`_client/`**: Contains the core client logic for the Langfuse SDK.
    -   **`langchain/`**: Contains the integration with the Langchain framework.

-   **`tests/`**: Contains all the tests for the `interactiveai` package. This directory is not included in the final distribution.

-   **`Makefile`**: A helper file with commands to simplify the development and release process.

-   **`pyproject.toml`**: The main configuration file for the project. It defines the project's metadata, dependencies, and build configuration.

-   **`README.md`**: This file. It is the main README for the GitHub repository.

-   **`README_pypi.md`**: The README file that is displayed on the PyPI package page.

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
