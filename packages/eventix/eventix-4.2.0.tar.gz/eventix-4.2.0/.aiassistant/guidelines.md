### Eventix Coding Guidelines

These guidelines capture the conventions already used in this repository and provide practical rules for implementing new code consistently.

#### Python and Tooling
- Python: target `^3.13` (see `pyproject.toml`). Use modern typing features (`list[int]`/`dict[str, Any]`, `|` for unions, `Self`).
- Formatting and linting: use Ruff for both. Do not hand‑tune formatting; let Ruff decide based on `pyproject.toml`.
- Typical commands:
  - `ruff format` to auto-format the codebase
  - `ruff check --fix` to auto-fix lint issues
- Testing: `pytest` with CLI logging enabled; prefer small, focused tests. Use fixtures under `tests/fixtures` and `freezegun` for time‑dependent logic.

#### Imports and Module Structure
- Order imports in three groups: standard library, third‑party, local (`eventix.*`). Keep a blank line between groups.
- Prefer `from __future__ import annotations` for files that use forward references or heavy typing to reduce runtime typing overhead.
- Use absolute `eventix.*` imports inside the package.

#### Naming
- Modules and functions: `snake_case`.
- Classes and Exceptions: `CamelCase`.
- Constants: `UPPER_SNAKE_CASE`.
- Private helpers: prefix with a single underscore when appropriate.

#### Typing
- Add type hints for all public functions, methods, and important locals.
- Use `| None` for optionals and built‑in generics (`list[str]`, `dict[str, Any]`).
- Prefer `Literal`/`Enum` where constrained values exist (see `EventixTaskStatusEnum`).
- For Pydantic v2, construct/validate via `model_validate(...)` and serialize via `model_dump(...)`. When parsing HTTP responses containing JSON bytes, use `model_validate_json(...)`.

#### Pydantic Models
- Base models derive from `pydantic_db_backend_common.pydantic.BackendModel` when persisted; otherwise from `pydantic.BaseModel`.
- Define field defaults with `Field(...)` and use `default_factory` for timestamps and collections to avoid shared mutables.
- Use timezone‑aware datetimes; prefer `utcnow()` from `pydantic_db_backend_common.utils` over `datetime.utcnow()`.
- Avoid deprecated Pydantic v1 methods (e.g., `parse_obj`); use v2 idioms.

#### Date and Time
- All datetimes are UTC. Ensure timezone information is present. When accepting naive datetimes, normalize to UTC (see handling in `functions/core.py:task.make_task_model`).

#### Logging
- Never use `print` for runtime diagnostics. Use `logging.getLogger(__name__)` and the shared `setup_logging` helper from `eventix.functions.tools` for CLI/worker setup.
- Prefer structured, short messages. On caught exceptions that propagate or are terminal, use `log.exception(e)` to include tracebacks; otherwise, use `log.debug`/`log.info`/`log.warning`/`log.error` appropriately.

#### Error Handling
- For HTTP calls made through `EventixClient.interface` (`LsRestClient`), wrap responses in `raise_errors(response, backend_exceptions)` to convert error payloads into rich exceptions (see `eventix.functions.errors`).
- Use the project’s exception types from `eventix.exceptions` (e.g., `TaskNotRegistered`, `NoTaskFoundForUniqueKey`). Don’t silently swallow exceptions; either handle, log, and persist status, or re‑raise.

#### HTTP/Client Usage
- All client interactions should go through `EventixClient` or subclasses. Set base URL via configuration (`EventixClient.config`) and avoid hardcoding URLs.
- Always include the current `namespace` using the `namespace_context` context manager; do not pass it manually unless explicitly required by the API.

#### Contexts
- Use context managers/providers from `eventix.contexts` to propagate request/workflow state:
  - `namespace_context`, `namespace_context_var`
  - `delay_tasks_context`/`delay_tasks_context_var`
  - `task_priority_context` and providers for worker/task IDs
- Wrap code that depends on these values with the appropriate context to keep state thread‑ and async‑safe.

#### Tasks and Scheduling
- Define tasks using `@eventix.functions.core.task(...)`. The decorator returns an `EventixTask` wrapper with:
  - `.delay(...)` to enqueue/schedule tasks (respects `delay_tasks_context`).
  - `.run(...)` to execute immediately with argument type restoration.
- Use unique keys via `unique_key_generator` when idempotency is required; the scheduler will update existing tasks with the same unique key.
- Priority note: the system uses ascending sort; thus negative of the logical priority is stored. Use provided APIs and do not manually negate priorities outside of `EventixTask`.

#### Worker Behavior
- Long‑running workers (see `functions/task_worker.py`) must:
  - Periodically call `task_next_scheduled()` and process tasks.
  - Handle connection errors gracefully and retry with backoff (simple `time.sleep` currently used).
  - Persist results or errors back to the backend via `task_write_back`.

#### Serialization and Persistence
- When sending models over HTTP, serialize with `.model_dump()`.
- When receiving JSON bytes, prefer `TEventixTask.model_validate_json(response.content)`.
- Be mindful of expiration semantics (`error_expires`, `result_expires`, `expires`) and status transitions defined in `eventix/pydantic/task.py` and server handlers.

#### Tests
- Place tests under `tests/` mirroring package structure. Use existing fixtures (`tests/fixtures`) for backend, worker, and client interactions.
- Do not rely on real time in tests; use `freezegun` or manipulate scheduling timestamps.
- For HTTP tests, use `httpx` and test routers/clients at the boundary (`tests/client`, `tests/router`).

#### Style and Documentation
- Keep functions small and composable. Prefer explicit over implicit behavior.
- Add short, focused docstrings for public modules, classes, and methods that are part of the library surface area. Follow Google- or NumPy‑style docstrings if needed; consistency within a file is more important than the chosen style.
- Keep comments concise and only where they add clarity beyond code.

#### Commit Hygiene
- One logical change per commit. Include a clear summary and brief body explaining the why when non‑obvious.

#### Examples

```python
from __future__ import annotations

import logging
from typing import Any

from eventix.functions.core import task
from eventix.pydantic.task import TEventixTask

log = logging.getLogger(__name__)


def _unique(*args, **kwargs) -> str:
    return f"mytask:{kwargs.get('key')}"


@task(unique_key_generator=_unique, store_result=True)
def mytask(key: str, payload: dict[str, Any]) -> str:
    log.info("Processing %s", key)
    return "ok"


def schedule_example() -> TEventixTask:
    # Respects contexts set via EventixClient.config(...)
    return mytask.delay(key="42", payload={"a": 1})
```
