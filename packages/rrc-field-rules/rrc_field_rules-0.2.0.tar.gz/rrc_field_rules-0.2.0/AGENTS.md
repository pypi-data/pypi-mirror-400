# AGENTS.md - Python Script & CLI Configuration

## 1. Project Architecture & Standards
**Philosophy:** We follow "Hypermodern Python" standards. Code must be modular, type-safe, and testable.
**Critical Rule:** NO MONOLITHS. Logic must be split into small, single-purpose files within `src/`.

### Directory Structure (Src Layout)
The `src/` layout is mandatory to prevent import errors and ensure tests run against the installed package, not the local file.

```text
project_root/
├── pyproject.toml       # SINGLE source of truth (Deps, Config, Build)
├── uv.lock              # Lockfile (if using uv)
├── .python-version      # Python version pin
├── README.md
├── src/
│   └── project_name/    # Actual package
│       ├── __init__.py
│       ├── __main__.py  # Entry point (allows `python -m project_name`)
│       ├── cli.py       # Typer/Click definition (Interface Layer)
│       ├── core.py      # Business logic orchestration
│       ├── config.py    # Pydantic settings
│       └── utils/       # Small, pure functions
│           ├── __init__.py
│           └── fs.py
└── tests/
    ├── __init__.py
    ├── conftest.py      # Pytest fixtures
    └── test_core.py
```

## 2. Tech Stack & Tooling
* **Package Manager:** `uv` (preferred) or `poetry`. Do not use `pip` + `requirements.txt` unless strictly restricted.
* **Linter/Formatter:** `ruff`. (Replaces Black, Isort, Flake8).
    * *Configuration:* Line length 88, double quotes, strict import sorting.
* **Type Checking:** `mypy` or `pyright`. Strict mode enabled.
* **CLI Framework:** `typer` (Standard) or `click`. Avoid `argparse`.
* **Configuration:** `pydantic-settings`. Do not use `os.getenv` directly in logic files.

## 3. Design Patterns for Modularity
**Constraint:** Files must be small (<200 lines). If a file grows larger, split it.

1.  **Interface vs. Implementation:**
    * `cli.py` handles arguments and printing. It **never** contains business logic. It imports from `core.py`.
    * *Bad:* `def main(): # logic here`
    * *Good:* `def main(): core.process_data(args)`

2.  **The "Runnable Module" Pattern:**
    * The script is executed via `__main__.py`.
    * User runs: `python -m project_name` or `uv run project_name`.
    * `__main__.py` content:
        ```python
        from .cli import app
        
        if __name__ == "__main__":
            app()
        ```

3.  **Dependency Injection:**
    * Functions should accept dependencies (like db connections or config objects) as arguments rather than instantiating them globally.

## 4. Coding Standards
* **Type Hints:** 100% coverage required. Use `typing.Annotated` for CLI args.
* **Error Handling:** Use custom exceptions defined in `exceptions.py`. Never catch bare `Exception`.
* **Docstrings:** Google Style. Required for all public modules, classes, and functions.

## 5. Testing Strategy
* **Framework:** `pytest`.
* **Structure:** Tests must mirror the `src/` structure.
* **Coverage:** 90%+ branch coverage.
* **Mocking:** Use `pytest-mock` (`mocker` fixture). Never make real network calls in tests.

## 6. Agent Workflow
1.  **Init:** If `pyproject.toml` is missing, generate it with `uv init` or standard PEP 621 metadata.
2.  **Code:** When asked to write a script, immediately structure it into `src/project_name/`. Do not dump code into a root `script.py`.
3.  **Refactor:** If you see a function with >3 branches or >20 lines, suggest extracting a helper function.