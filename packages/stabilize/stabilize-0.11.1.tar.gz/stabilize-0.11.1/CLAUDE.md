# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Stabilize is a lightweight Python workflow execution engine implementing a message-driven DAG orchestration system. It provides the execution layer for building and running complex pipelines with parallel and sequential stage execution.

## Common Commands

```bash
# Development
make install-dev           # Install dev dependencies
make check                 # Run lint + type-check + tests (full validation)

# Testing
make test                  # Run all unit tests (both SQLite and PostgreSQL backends)
make test-sqlite           # SQLite backend only (no Docker required)
make test-postgres         # PostgreSQL backend only (requires Docker)
make golden-tests          # Golden standard integration tests
python -m pytest tests/path/to/test.py::test_function  # Run single test

# Linting & Type Checking
make lint                  # Run ruff linter
make lint-fix              # Auto-fix linting issues
make type-check            # Run mypy type checker
```

## Architecture

### Message-Driven DAG Execution

The core pattern: stages form a DAG, and execution progresses via queued messages processed by handlers.

```
Workflow → Stages (DAG) → Tasks (sequential within stage)
    ↓
Message Queue → Handler dispatches → State updates → Next messages
```

**Key Message Types** (`src/stabilize/queue/messages.py`):
- StartWorkflow → StartStage → StartTask → RunTask → CompleteTask → CompleteStage → CompleteWorkflow

### Handler Registry Pattern

Each message type has a dedicated handler in `src/stabilize/handlers/`:
- `StartWorkflowHandler` - finds initial stages (no requisites)
- `StartStageHandler` - merges upstream outputs into stage context
- `RunTaskHandler` - executes task via TaskRegistry, captures outputs
- `CompleteStageHandler` - triggers downstream stages or synthetic stages
- `CompleteWorkflowHandler` - finalizes execution

### Data Flow Between Stages

Stage dependencies defined via `requisite_stage_ref_ids`. Outputs flow downstream:
1. Task outputs → `StageExecution.outputs`
2. `StartStageHandler` calls `get_merged_ancestor_outputs()` to collect upstream outputs
3. Merged outputs available in downstream stage `context`
4. PythonTask exposes merged context as `INPUT` dict

See `docs/stage-data-flow.md` for detailed documentation.

### Key Directory Structure

| Directory | Purpose |
|-----------|---------|
| `src/stabilize/models/` | Core data models (Workflow, StageExecution, TaskExecution, WorkflowStatus) |
| `src/stabilize/handlers/` | Message handlers implementing execution logic |
| `src/stabilize/queue/` | Message queue interface and processor |
| `src/stabilize/tasks/` | Task implementations (Shell, Python, HTTP, Docker, SSH) and registry |
| `src/stabilize/persistence/` | Store abstraction (SQLite, PostgreSQL, Memory backends) |
| `src/stabilize/dag/` | DAG graph construction and topological sort |
| `src/stabilize/stages/` | Synthetic stage builders (before/after stages) |

### Persistence Layer

Abstract `WorkflowStore` (`src/stabilize/persistence/store.py`) with implementations:
- **SQLite** - file-based, WAL mode, thread-safe (development)
- **PostgreSQL** - connection pooling (production)
- **In-Memory** - for testing

Atomic transactions bind store + queue operations together.

### Task System

All tasks implement `Task` interface (`src/stabilize/tasks/interface.py`) and return `TaskResult`.

**Built-in Tasks**:
- `ShellTask` - shell commands (context: `command`, `cwd`, `timeout`)
- `PythonTask` - Python code (context: `script`/`script_file`/`module`, `function`, `inputs`)
- `HTTPTask` - HTTP requests (context: `url`, `method`, `json`, `bearer_token`)
- `DockerTask` - containers (context: `image`, `command`, `env`, `volumes`)
- `SSHTask` - remote execution (context: `host`, `user`, `command`, `private_key`)

### Synthetic Stages

Before/after stages injected around regular stages for setup, cleanup, validation, or failure handling. Built via `StageGraphBuilder` (`src/stabilize/stages/builder.py`).

## Testing Notes

- SQLite tests work standalone; PostgreSQL tests require Docker
- Test fixtures in `tests/conftest.py`
- Golden standard tests in `golden_standard_tests/` exercise both backends
- Examples in `examples/` directory demonstrate all task types

## Technology Stack

- Python 3.11+ with Pydantic for validation
- ULID for unique IDs
- structlog for structured logging
- OpenTelemetry for tracing
- ruff for linting, mypy for type checking
