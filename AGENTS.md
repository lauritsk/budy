# Budy Development Guidelines

This document provides instructions for agents and developers working on the `budy` codebase.

## 1. Environment & Commands

This project uses `uv` for dependency management and `mise` for task execution.

### Setup
Ensure `uv` and `mise` are installed.
```bash
mise install
```

### Common Commands
All commands should be run via `mise` to ensure the correct environment and tool versions are used.

- **Linting**: Check code for style and errors.
  ```bash
  mise run lint
  ```
  (Runs `ruff check`)

- **Type Checking**: Verify type hints.
  ```bash
  mise run typecheck
  ```
  (Runs `ty check` - likely a wrapper or alias for a type checker, ensure `ty` is installed via mise)

- **Testing**: Run the test suite.
  ```bash
  mise run test
  ```
  (Runs `uv run pytest`)

- **Run Single Test**:
  ```bash
  uv run pytest tests/test_transactions.py::test_add_transaction
  ```

- **Build**: Build the package.
  ```bash
  mise run build
  ```

- **Docs**: Generate documentation.
  ```bash
  mise run generate-docs
  ```

- **CI Loop**: Run all checks (lint, types, tests, build).
  ```bash
  mise run check
  ```

## 2. Code Style & Conventions

### Formatting & Linting
- Follow standard Python formatting (Black/Ruff style).
- **Line Length**: Adhere to the project's configuration (likely 88 or 100 chars).
- **Quotes**: Use double quotes `"` for strings.
- **Imports**: Grouped and sorted:
  1. Standard Library
  2. Third-Party
  3. Local Application (`budy.xxx`)
  *Use absolute imports for local modules.*

### Type Hints
- **Strict Typing**: All functions and methods must have type hints.
- **Syntax**: Use modern Python 3.10+ syntax:
  - `list[str]` instead of `List[str]`
  - `str | None` instead of `Optional[str]`
- **Models**: Use `SQLModel` for database entities and schemas.

### Naming Conventions
- **Classes**: `PascalCase` (e.g., `Transaction`, `BudgetReport`).
- **Functions/Variables**: `snake_case` (e.g., `get_transactions`, `total_amount`).
- **Files**: `snake_case` (e.g., `transaction.py`, `utils.py`).
- **Constants**: `UPPER_CASE` (e.g., `DEFAULT_CURRENCY`).

### Architecture & Patterns
- **Directory Structure**:
  - `src/budy/services/`: Business logic (pure functions, database operations).
  - `src/budy/views/`: CLI commands and view logic.
  - `src/budy/schemas.py`: Data models and Pydantic/SQLModel schemas.
  - `tests/`: Pytest suite.

- **Dependency Injection**:
  - Pass `Session` objects explicitly to service functions.
  - Use keyword-only arguments for service functions to prevent argument swapping errors.
  ```python
  def create_transaction(*, session: Session, amount: int) -> Transaction:
      ...
  ```

- **Money Handling**:
  - **Storage**: Store monetary values as `int` (cents) in the database.
  - **Logic/Display**: Convert to `float` or `Decimal` when presenting to the user or performing complex calculations that require it.

- **Database**:
  - Use `SQLModel` for ORM interactions.
  - Prefer `select(Model).where(...)` syntax for queries.

### Error Handling
- Use specific exceptions (e.g., `ValueError`) with descriptive messages.
- Fail fast with guard clauses.

### Testing
- **Framework**: `pytest`.
- **Property-based Testing**: Use `hypothesis` for logic that handles user input or data processing.
- **CLI Testing**: Use `typer.testing.CliRunner`.
- **Fixtures**: Use `conftest.py` for shared fixtures.
- **Database Tests**: Ensure tests isolate database state (e.g., `reset_db` helper or transaction rollback fixtures).

## 3. Example Service Function
```python
from sqlmodel import Session
from budy.schemas import Transaction

def do_something(*, session: Session, param: str) -> list[Transaction]:
    """Description of what this does."""
    # Logic here
    return []
```

<!-- BEGIN BEADS INTEGRATION v:1 profile:minimal hash:ca08a54f -->
## Beads Issue Tracker

This project uses **bd (beads)** for issue tracking. Run `bd prime` to see full workflow context and commands.

### Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim  # Claim work
bd close <id>         # Complete work
```

### Rules

- Use `bd` for ALL task tracking — do NOT use TodoWrite, TaskCreate, or markdown TODO lists
- Run `bd prime` for detailed command reference and session close protocol
- Use `bd remember` for persistent knowledge — do NOT use MEMORY.md files

## Session Completion

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   bd dolt push
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds
<!-- END BEADS INTEGRATION -->
