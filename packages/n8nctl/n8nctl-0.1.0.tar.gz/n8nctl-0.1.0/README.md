# n8n CLI

A command-line tool for managing n8n Cloud workflows.

## Installation

### Global Installation (Recommended)

```bash
uv tool install .
```

### Configuration

Create a credentials file with your n8n API credentials. The file can be placed in:
- Your current working directory as `.env` (project-specific)
- `~/.config/n8n-cli/config` (global configuration)

**Project-specific (`.env` in current directory):**
```bash
N8N_API_KEY=your-api-key
N8N_INSTANCE_URL=https://your-instance.app.n8n.cloud/api/v1
```

**Global (`~/.config/n8n-cli/config`):**
```bash
N8N_API_KEY=your-api-key
N8N_INSTANCE_URL=https://your-instance.app.n8n.cloud/api/v1
```

Alternatively, set environment variables:
```bash
export N8N_API_KEY="your-api-key"
export N8N_BASE_URL="https://your-instance.app.n8n.cloud/api/v1"
```

### Development Installation

For local development:
```bash
uv sync
```

## Development

```bash
# Install with dev dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install

# Clean install tool globally (clears cache for fresh build)
uv run poe install

# Quick reinstall without cache clean (faster)
uv run poe reinstall

# Run tests
uv run poe test

# Run code quality checks
uv run poe check        # lint + typecheck + test
uv run poe lint         # just linting
uv run poe typecheck    # just type checking
uv run poe format       # format code

# Run pre-commit hooks manually
uv run pre-commit run --all-files
```

## Usage

```bash
n8n --help
```

## Examples

### Workflow Management

**List all workflows:**
```bash
n8n workflow list
n8n workflow list -v  # verbose output with more details
```

**View workflow details:**
```bash
n8n workflow view "My Workflow"
```

**Activate/deactivate workflows:**
```bash
n8n workflow activate "My Workflow"
n8n workflow deactivate "My Workflow"
```

**Pull workflows to local files:**
```bash
n8n workflow pull                    # Pull all workflows
n8n workflow pull "My Workflow"      # Pull specific workflow
n8n workflow pull --project "Sales"  # Pull all workflows from a project
```

**Push local workflow to cloud:**
```bash
n8n workflow push workflow.json
n8n workflow push workflow.json --update  # Update existing workflow
```

**Create new workflow:**
```bash
n8n workflow create new_workflow.json
```

**Compare local and cloud versions:**
```bash
n8n workflow diff workflow.json
```

**Move workflow to different project:**
```bash
n8n workflow move "My Workflow" --project "Marketing"
```

**Open workflow in browser:**
```bash
n8n workflow open "My Workflow"
```

**Delete workflow:**
```bash
n8n workflow delete "My Workflow"
```

### Execution Management

**List recent executions:**
```bash
n8n execution list
n8n execution list --workflow "My Workflow"  # Filter by workflow
n8n execution list --limit 50                # Show more results
```

**View execution details:**
```bash
n8n execution view <execution-id>
```

**Download execution data:**
```bash
n8n execution download <execution-id>
n8n execution download <execution-id> -o execution.json
```

**Retry failed execution:**
```bash
n8n execution retry <execution-id>
```

### Project Management

**List all projects:**
```bash
n8n project list
```

**View project details:**
```bash
n8n project view "Sales"
```

### User & Member Management

**List users:**
```bash
n8n user list
```

**Invite user:**
```bash
n8n user invite user@example.com --role member
n8n user invite admin@example.com --role admin
```

**Remove user:**
```bash
n8n user remove user@example.com
```

**List project members:**
```bash
n8n member list --project "Sales"
```

**Add member to project:**
```bash
n8n member add user@example.com --project "Sales" --role editor
```

**Remove member from project:**
```bash
n8n member remove user@example.com --project "Sales"
```

## Shell Completion

Enable tab completion for workflows, projects, and file paths:

### Installation

**Automatic (recommended):**
```bash
n8n --install-completion
```

Follow the shell-specific instructions. You may need to restart your shell.

**Manual setup:**

**Bash:**
```bash
eval "$(n8n --show-completion bash)"
# Add to ~/.bashrc for persistence
```

**Zsh:**
```bash
eval "$(n8n --show-completion zsh)"
# Add to ~/.zshrc for persistence
```

**Fish:**
```bash
n8n --show-completion fish > ~/.config/fish/completions/n8n.fish
```

### What Gets Completed

- **Workflow names:** `n8n workflow view <TAB>` shows your workflows
- **Project names:** `n8n project view <TAB>` shows your projects
- **File paths:** `n8n workflow diff <TAB>` shows .json files

**Note:** The `n8n` command must be available in your PATH for completion to work. Either activate the virtual environment (`source .venv/bin/activate`) or install globally.
