# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

n8n CLI is a command-line tool for managing n8n Cloud workflows, inspired by GitHub's `gh` CLI. It enables terminal-based workflow management with a local-first editing experience: list/view workflows, pull to local JSON files for version control, push changes back to cloud, diff local vs cloud versions, and manage projects, users, executions, and members.

## Development Commands

### Environment Setup
```bash
# Install dependencies
uv sync

# Install pre-commit hooks (required for development)
uv run pre-commit install
```

### Running the CLI
```bash
# During development (from repo root)
uv run n8n --help
uv run n8n workflow list

# After global installation
n8n --help
```

### Testing
```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=n8n_cli --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_config.py

# Run specific test
uv run pytest tests/test_config.py::TestN8nConfig::test_load_from_local_env

# Run tests matching pattern
uv run pytest -k "workflow"
```

### Code Quality
```bash
# Run all pre-commit hooks manually
uv run pre-commit run --all-files

# Run specific tools
uv run ruff check src/n8n_cli/        # Lint
uv run ruff check --fix src/n8n_cli/  # Lint with auto-fix
uv run ruff format src/n8n_cli/       # Format
uv run mypy src/n8n_cli/              # Type check
```

### Configuration

Configuration hierarchy (highest to lowest priority):
1. Environment variables (`N8N_API_KEY`, `N8N_INSTANCE_URL`)
2. Local `.env` file (project-specific)
3. Global `~/.config/n8n-cli/config` file
4. Defaults (None)

## Architecture

### Hub-and-Spoke API Client Pattern

The codebase uses a **hub-and-spoke architecture** for the API client:

- **Hub**: `APIClient` (in `client/core.py`) manages the shared `httpx.Client` instance with connection pooling, timeout, and authentication headers
- **Spokes**: Resource classes (`WorkflowsResource`, `ExecutionsResource`, `ProjectsResource`, `UsersResource`) handle domain-specific API endpoints
- Resources are accessed as properties: `client.workflows`, `client.executions`, `client.projects`, `client.users`

**Example:**
```python
with APIClient(base_url=url, api_key=key) as client:
    workflows = client.workflows.list()      # WorkflowsResource
    executions = client.executions.list()    # ExecutionsResource
    projects = client.projects.list()        # ProjectsResource
```

**Benefits:**
- Single shared HTTP client (connection pooling)
- Clean separation of concerns (each resource owns its domain)
- Easy to extend (add new resources without modifying hub)
- Consistent retry logic via `@retry` decorators on resource methods

### Error Handling

**Exception Hierarchy** (in `client/exceptions.py`):
```
N8NAPIError (base)
├── AuthenticationError (401)
├── NotFoundError (404)
├── ValidationError (400/422)
└── ServerError (5xx)
```

- `handle_response(response)` utility converts HTTP errors to domain exceptions and **extracts error messages from API response bodies**
- Error messages are extracted from common fields: `message`, `error`, `detail`
- If extraction fails, shows raw response text (first 200 chars)
- All API methods raise specific exceptions for different failure modes
- Retry logic: 3 attempts with exponential backoff (2s, 4s, 8s) for transient errors

### Data Models

**Pydantic models** (in `client/models/`) provide type-safe API responses:
- `Workflow`: Core workflow data (id, name, active, nodes, connections, settings, etc.)
- `Execution`: Execution data (id, workflow_id, status, start/finish times, data)
- `Project`: Project data (id, name, type, created_at)
- `User`: User data (id, email, firstName, lastName, role)

Models use `alias_generator=to_camel` to map Python snake_case to API camelCase automatically.

### Utility Functions

**Core utilities** (in `utils.py`):
- `sanitize_filename(name)`: Converts workflow names to safe kebab-case filenames
- `find_workflow_file(name_or_path)`: Smart file resolution (accepts path or workflow name)
- `detect_project_context()`: Auto-detects project from `.n8n/config.json` or directory structure
- `save_workflow(workflow, project_name)`: Saves workflow JSON to proper directory structure

**Directory structure for workflows:**
```
workflows/                    # Base directory
├── my-workflow.json         # No project
└── my-project/              # Project-specific
    └── project-workflow.json
```

### Workflow Push Field Restrictions

The n8n API has **strict field requirements** for workflow updates. When pushing workflows:

**Writable fields** (only these are sent):
- `name` - Workflow name
- `nodes` - Node definitions
- `connections` - Node connections
- `settings` - Workflow settings

**Read-only fields** (automatically filtered out):
- `id` - Used to identify the workflow in the URL, not sent in body
- `active` - Must be changed via separate activate/deactivate endpoints
- `tags` - Read-only in update operations
- `createdAt`, `updatedAt` - Timestamps managed by API
- `projectId` - Project assignment is read-only

The `workflow push` command (in `commands/workflow.py`) uses an **allowlist approach** to ensure only writable fields are sent to the API.

### Command Pattern

**CLI commands** (in `commands/`) follow a consistent pattern:
1. Load config via `N8nConfig.load()`
2. Validate credentials exist
3. Create `APIClient` context manager
4. Call resource methods
5. Display results with progressive verbosity

**Verbosity levels** (`-v` flag, count=True):
- `-v`: Basic details (workflow nodes, execution data)
- `-vv`: More details (workflow settings, execution steps)
- `-vvv`: Full details (all metadata)
- `-vvvv`: Debug output (raw API responses)

### Shell Completion

**Dynamic completion** (in `completion.py`):
- `complete_workflows()`: Fetches workflow names from API
- `complete_projects()`: Fetches project names from API
- `complete_workflow_files()`: File completion for `.json` files
- Applied via `autocompletion=` parameter in Typer commands
- Silent error handling (returns empty list on failures, never breaks commands)

## Testing Philosophy

From `.planning/PROJECT.md`:
> Emphasis on code quality over just test coverage. Tests should be high-quality with minimal mocking and minimal duplication, not just hitting coverage metrics.

**Current approach:**
- Coverage requirement: 79% (enforced by pre-commit hook)
- Comprehensive test suite with 268 tests
- Mock `time.sleep` globally to avoid retry delays (tests run in ~1s instead of ~69s)
- Use `pytest-httpx` for HTTP mocking instead of generic mocks
- Use `pytest-mock` and `monkeypatch` for targeted test doubles

## Key Patterns

### Resource Methods Always Use Retry Logic
Every API method in resource classes has `@retry` decorator with:
- 3 attempts
- Exponential backoff (2s, 4s, 8s)
- Retry on: `httpx.HTTPError`, `ConnectionError`, `ServerError`

### Commands Always Use Context Managers
```python
with APIClient(base_url=config.instance_url, api_key=config.api_key) as client:
    # API calls
```
This ensures proper cleanup of HTTP connections.

### Input Resolution is Flexible
Many commands accept either IDs, names, or file paths:
- `n8n workflow view "My Workflow"` (name)
- `n8n workflow view wf_abc123` (ID)
- `n8n workflow push workflow.json` (file path)
- `n8n workflow push "My Workflow"` (name, searches in workflows/)

### Field Filtering
The n8n API supports field filtering (not fully implemented yet):
- Resource methods can filter which fields are returned
- Reduces payload size for large workflows
- Pattern: `fields=["id", "name", "active"]`

## Pre-commit Hooks

The pre-commit configuration enforces:
- Standard checks (large files, private keys, merge conflicts)
- Ruff linting and formatting (replaces Black, isort, Flake8, pyupgrade)
- Mypy type checking
- Pytest with 79% coverage requirement

**To bypass hooks** (only when necessary):
```bash
git commit --no-verify
```

## Important Notes

- **Python version**: 3.12+ (uses modern patterns like `Self`, union types with `|`)
- **Dependencies**: Typer (CLI), Pydantic (models), httpx (HTTP), tenacity (retry), python-dotenv (config)
- **API**: n8n Cloud API v1 (base URL format: `https://instance.app.n8n.cloud/api/v1`)
- **Testing**: Global `time.sleep` mock in `conftest.py` eliminates retry delays
- **Project status**: All 7 phases complete (see `.planning/ROADMAP.md`)
