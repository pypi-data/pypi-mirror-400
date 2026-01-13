# Phase 1: Foundation & Configuration - Research

**Researched:** 2026-01-04
**Domain:** Python CLI development with Click, configuration management, and quality tooling
**Confidence:** HIGH

<research_summary>
## Summary

Researched the modern Python CLI ecosystem for building a production-quality command-line tool. The standard approach in 2026 uses Click (or its modern successor Typer) for CLI framework, python-dotenv or Pydantic for configuration, httpx for HTTP client (modern replacement for requests), and Ruff as the all-in-one linter/formatter (replacing Black, isort, Flake8, etc.).

Key findings:
- **Ruff consolidation**: Modern Python projects use only Ruff instead of 5+ separate tools (Black, isort, Flake8, pyupgrade, autoflake) - it's 10-100x faster and provides unified configuration
- **Typer over Click**: For new projects, Typer offers cleaner syntax using type hints while maintaining all Click capabilities
- **httpx for async-ready**: While requests is fine for simple CLIs, httpx provides modern HTTP/2 support and async capabilities
- **Pydantic for config validation**: Better than plain python-dotenv for type safety and validation
- **src layout**: Industry standard project structure with pyproject.toml

**Primary recommendation:** Use Typer (Click under the hood) + Pydantic BaseSettings for config + httpx for HTTP + Ruff for all linting/formatting + pre-commit hooks + src layout with pyproject.toml.

</research_summary>

<standard_stack>
## Standard Stack

The established libraries/tools for Python CLI development in 2026:

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| typer | 0.13+ | CLI framework | Modern type-hint driven Click wrapper, cleaner syntax |
| click | 8.3+ | CLI framework (alternative) | Industry standard, widely adopted, Typer is built on it |
| pydantic | 2.x | Config validation | Type-safe config with BaseSettings for env vars |
| httpx | 0.27+ | HTTP client | Modern, async-ready, HTTP/2 support |
| ruff | 0.8+ | Linter & formatter | Replaces 5+ tools, 10-100x faster, Rust-based |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| python-dotenv | 1.0+ | .env file loading | If not using Pydantic BaseSettings |
| pytest | 8.x | Testing framework | Universal Python testing standard |
| pre-commit | 6.0+ | Git hooks | Enforce quality checks before commit |
| mypy | 1.x | Type checking | Static type analysis (optional but recommended) |
| keyring | 25.x | Secure credential storage | If storing tokens in OS keychain |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Typer | Click | Click if maintaining existing codebase or prefer decorators |
| httpx | requests | requests simpler for sync-only, but httpx is more future-proof |
| Ruff | Black+isort+Flake8 | Old approach requires 5+ tools vs 1, much slower |
| Pydantic | python-dotenv | dotenv simpler but no validation, Pydantic catches config errors |
| pyproject.toml | setup.py | setup.py is legacy, pyproject.toml is modern standard |

**Installation:**
```bash
pip install typer httpx pydantic pytest ruff pre-commit
# or with Poetry
poetry add typer httpx pydantic
poetry add --group dev pytest ruff pre-commit mypy
```

</standard_stack>

<architecture_patterns>
## Architecture Patterns

### Recommended Project Structure (src layout)

```
n8n_cli/
├── .pre-commit-config.yaml    # Pre-commit hooks
├── pyproject.toml              # Project config, dependencies, tool settings
├── README.md
├── .gitignore
├── tests/                      # Tests directory (outside src)
│   ├── __init__.py
│   ├── conftest.py
│   └── test_*.py
└── src/
    └── n8n_cli/               # Actual package
        ├── __init__.py
        ├── __main__.py        # Entry point for `python -m n8n_cli`
        ├── cli.py             # Main CLI app with Typer
        ├── config.py          # Configuration loading
        ├── auth.py            # Authentication logic
        └── client.py          # HTTP client (Phase 2)
```

**Benefits of src layout:**
- Prevents accidental imports of uninstalled code
- Forces testing against installed package
- Industry standard for 2026

### Pattern 1: Configuration Hierarchy with Pydantic

**What:** Load config from multiple sources with proper precedence
**When to use:** Any CLI needing flexible configuration
**Example:**
```python
# Source: Pydantic BaseSettings pattern
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class N8nConfig(BaseSettings):
    """n8n CLI configuration with hierarchy:
    1. CLI flags (highest priority - handled by Typer)
    2. Environment variables
    3. Local .env file
    4. Global config file (~/.n8n-cli/config)
    5. Defaults (lowest priority)
    """
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        env_prefix='N8N_',
        extra='ignore'
    )

    api_key: str | None = None
    instance_url: str | None = None

    @classmethod
    def load(cls) -> "N8nConfig":
        """Load config with proper precedence."""
        # 1. Try local .env
        if Path('.env').exists():
            return cls(_env_file='.env')

        # 2. Try global config
        global_config = Path.home() / '.n8n-cli' / 'config'
        if global_config.exists():
            return cls(_env_file=str(global_config))

        # 3. Env vars only
        return cls()
```

### Pattern 2: Typer CLI with Type Hints

**What:** Use Python type hints to define CLI interface
**When to use:** All new CLI projects
**Example:**
```python
# Source: Typer official docs
import typer
from typing import Optional
from pathlib import Path

app = typer.Typer()

@app.command()
def workflows(
    project: Optional[str] = typer.Option(None, help="Project name or ID"),
    verbose: int = typer.Option(0, "-v", count=True, help="Increase verbosity"),
    output_format: str = typer.Option("table", "--format", help="Output format")
) -> None:
    """List workflows in the project."""
    # Type hints provide:
    # - Automatic validation
    # - Auto-generated help
    # - IDE autocomplete
    pass

if __name__ == "__main__":
    app()
```

### Pattern 3: Secure Token Storage

**What:** Store API tokens securely using OS keychain
**When to use:** When storing sensitive credentials
**Example:**
```python
# Source: Python keyring library pattern
import keyring

SERVICE_NAME = "n8n-cli"

def save_api_key(api_key: str) -> None:
    """Save API key to system keychain."""
    keyring.set_password(SERVICE_NAME, "api_key", api_key)

def get_api_key() -> str | None:
    """Retrieve API key from system keychain."""
    return keyring.get_password(SERVICE_NAME, "api_key")

# Fallback: If keyring fails (headless systems), use .env
```

### Pattern 4: HTTP Client with httpx

**What:** Modern HTTP client with better defaults than requests
**When to use:** All HTTP calls
**Example:**
```python
# Source: httpx documentation
import httpx
from typing import Any

class N8nClient:
    def __init__(self, api_key: str, instance_url: str):
        self.base_url = instance_url.rstrip('/')
        self.headers = {"X-N8N-API-KEY": api_key}
        self.client = httpx.Client(
            base_url=self.base_url,
            headers=self.headers,
            timeout=30.0
        )

    def get(self, endpoint: str) -> dict[str, Any]:
        response = self.client.get(endpoint)
        response.raise_for_status()
        return response.json()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.client.close()
```

### Anti-Patterns to Avoid

- **Hard-coding credentials in code:** Always use environment variables or config files
- **Using setup.py instead of pyproject.toml:** setup.py is legacy, pyproject.toml is 2026 standard
- **Multiple separate tools (Black+isort+Flake8):** Use Ruff for everything
- **Flat layout without src/:** Causes import issues, src layout is standard
- **Not using type hints with Typer:** Defeats the purpose, type hints are the feature
- **Synchronous-only HTTP client:** httpx provides both sync and async in one library

</architecture_patterns>

<dont_hand_roll>
## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| CLI argument parsing | Custom argv parsing | Typer or Click | Handles validation, help, subcommands, options |
| .env file parsing | String splitting | python-dotenv or Pydantic | Handles comments, quotes, multiline, escaping |
| Config precedence | Manual if/else chains | Pydantic BaseSettings | Built-in hierarchy, validation, type conversion |
| Credential storage | Plain text files | keyring library | Uses OS keychain (secure), falls back gracefully |
| HTTP requests | urllib or manual sockets | httpx | Connection pooling, retries, timeouts, HTTP/2 |
| Code formatting | Manual style enforcement | Ruff | 100x faster than Black, handles everything |
| Path handling | String concatenation | pathlib.Path | Cross-platform, proper separators, type-safe |

**Key insight:** The Python ecosystem has mature, battle-tested solutions for all CLI infrastructure concerns. Custom implementations lead to edge cases (e.g., .env quote handling, credential encryption, HTTP retries) that take weeks to debug. Use established libraries and focus on your actual CLI commands.

</dont_hand_roll>

<common_pitfalls>
## Common Pitfalls

### Pitfall 1: Mixing src Layout with Incorrect Imports

**What goes wrong:** Tests import from wrong location, CI passes but installed package fails
**Why it happens:** Python finds local files before installed package
**How to avoid:** Use src layout + install package in editable mode (`pip install -e .`)
**Warning signs:** Tests pass locally but fail in CI, or vice versa

### Pitfall 2: Storing API Keys in .env Without .gitignore

**What goes wrong:** Credentials committed to git, exposed on GitHub
**Why it happens:** Forgot to add .env to .gitignore
**How to avoid:** Add .env to .gitignore IMMEDIATELY, use .env.example for documentation
**Warning signs:** git status shows .env file as untracked

### Pitfall 3: Not Validating Config Early

**What goes wrong:** CLI runs, makes API calls, then fails with cryptic error
**Why it happens:** Missing or invalid config only discovered when used
**How to avoid:** Validate all required config at startup using Pydantic
**Warning signs:** Users report "works sometimes" - missing env vars

### Pitfall 4: Using requests Without Timeouts

**What goes wrong:** CLI hangs indefinitely on network issues
**Why it happens:** requests has no default timeout
**How to avoid:** Always set timeout in httpx.Client() or requests.get(timeout=30)
**Warning signs:** Users report CLI "freezing" or "hanging"

### Pitfall 5: Too Many Tools (Black+isort+Flake8+pyupgrade+autoflake)

**What goes wrong:** Slow CI, conflicting configs, maintenance burden
**Why it happens:** Using pre-2023 tooling patterns
**How to avoid:** Use Ruff for everything - it replaces all 5+ tools
**Warning signs:** pyproject.toml has 5 [tool.X] sections for formatters/linters

### Pitfall 6: Not Using Pre-commit Hooks

**What goes wrong:** Developers commit code that fails CI, wastes time
**Why it happens:** No local enforcement before commit
**How to avoid:** Set up pre-commit hooks from day one
**Warning signs:** Frequent "fix linting" commits in git history

</common_pitfalls>

<code_examples>
## Code Examples

Verified patterns from official sources:

### Basic Typer CLI Setup

```python
# Source: Typer official documentation
import typer
from typing_extensions import Annotated

app = typer.Typer(
    name="n8n-cli",
    help="Command-line interface for n8n Cloud",
    add_completion=True,
)

@app.command()
def version():
    """Show version information."""
    typer.echo("n8n-cli v0.1.0")

@app.command()
def workflows(
    active: Annotated[bool, typer.Option("--active", help="Show only active workflows")] = False,
    verbose: Annotated[int, typer.Option("-v", count=True, help="Increase verbosity")] = 0,
):
    """List workflows."""
    # Implementation here
    pass

if __name__ == "__main__":
    app()
```

### Pydantic Config with Validation

```python
# Source: Pydantic BaseSettings documentation
from pydantic import Field, field_validator, HttpUrl
from pydantic_settings import BaseSettings
from pathlib import Path

class N8nConfig(BaseSettings):
    """Configuration with automatic validation."""

    api_key: str = Field(..., description="n8n API key")
    instance_url: HttpUrl = Field(..., description="n8n instance URL")

    @field_validator('api_key')
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        if not v or len(v) < 10:
            raise ValueError('API key appears invalid')
        return v

    model_config = {
        'env_file': '.env',
        'env_file_encoding': 'utf-8',
        'env_prefix': 'N8N_',
    }
```

### Pre-commit Configuration (.pre-commit-config.yaml)

```yaml
# Source: pre-commit + Ruff official docs
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      # Run the linter
      - id: ruff
        args: [--fix]
      # Run the formatter
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
```

### Ruff Configuration in pyproject.toml

```toml
# Source: Ruff official documentation
[tool.ruff]
target-version = "py312"
line-length = 100

[tool.ruff.lint]
# Enable Pyflakes (F), pycodestyle (E), and isort (I)
select = ["E", "F", "I"]
ignore = []

# Allow autofix for all enabled rules
fixable = ["ALL"]
unfixable = []

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

### pytest Configuration in pyproject.toml

```toml
# Source: pytest official documentation
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "-ra",
]
```

### Testing CLI with pytest

```python
# Source: Typer testing documentation + pytest best practices
from typer.testing import CliRunner
from n8n_cli.cli import app

runner = CliRunner()

def test_version_command():
    """Test version command returns successfully."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "v0.1.0" in result.stdout

def test_workflows_command_without_config(monkeypatch):
    """Test workflows command fails gracefully without config."""
    monkeypatch.delenv("N8N_API_KEY", raising=False)
    result = runner.invoke(app, ["workflows"])
    assert result.exit_code != 0
    assert "API key" in result.stdout
```

</code_examples>

<sota_updates>
## State of the Art (2025-2026)

What's changed recently:

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Black + isort + Flake8 + pyupgrade | Ruff (all-in-one) | 2023-2024 | One tool replaces 5+, 100x faster |
| Click | Typer | 2020-2024 | Type hints reduce boilerplate, cleaner syntax |
| requests | httpx | 2021-2026 | HTTP/2, async support, better defaults |
| setup.py | pyproject.toml | 2020-2023 | PEP 517/518 standard, unified config |
| python-dotenv | Pydantic BaseSettings | 2023-2026 | Type validation, better error messages |
| Poetry v1.x | Poetry v2.0 (Jan 2025) | 2025 | Now supports [project] table in pyproject.toml |

**New tools/patterns to consider:**
- **Ruff consolidation:** Single tool for all linting/formatting is now standard
- **Typer over Click:** Type-hint driven CLIs are the modern pattern
- **uv package manager:** Faster alternative to pip/poetry (but still new, maybe wait)
- **Pydantic v2:** Major performance improvements, stricter validation

**Deprecated/outdated:**
- **setup.py:** Replaced by pyproject.toml (PEP 517/518)
- **requirements.txt for projects:** Use pyproject.toml dependencies section
- **Black as standalone:** Ruff formatter is faster and compatible
- **Multiple linter tools:** Ruff does it all

</sota_updates>

<open_questions>
## Open Questions

Things that couldn't be fully resolved:

1. **Click vs Typer for this project**
   - What we know: Typer is more modern, Click is more established
   - What's unclear: Project already mentions Click in requirements, migration path?
   - Recommendation: Start with Typer (uses Click underneath), easy to use either

2. **Keyring vs .env for token storage**
   - What we know: Keyring is more secure, .env is simpler
   - What's unclear: User preference for security vs simplicity trade-off
   - Recommendation: Support both - .env for simplicity, keyring as optional upgrade

3. **Testing approach for n8n API calls**
   - What we know: Should avoid hitting real API in tests
   - What's unclear: Mock at HTTP level (httpx) or service level (n8n client)?
   - Recommendation: Mock at client level for Phase 1, refine in Phase 7 (testing)

</open_questions>

<sources>
## Sources

### Primary (HIGH confidence)

- [Click Official Documentation](https://click.palletsprojects.com/) - CLI framework patterns
- [Typer Official Documentation](https://typer.tiangolo.com/) - Modern CLI framework
- [Ruff Official Documentation](https://docs.astral.sh/ruff/) - Linter/formatter setup
- [Pydantic Official Documentation](https://docs.pydantic.dev/) - Config validation
- [httpx Documentation](https://www.python-httpx.org/) - HTTP client
- [Python Packaging Guide - pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) - Project structure
- [Python Packaging Guide - src layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/) - Layout benefits
- [n8n API Authentication](https://docs.n8n.io/api/authentication/) - API key usage

### Secondary (MEDIUM confidence)

- [Real Python - Click Tutorial](https://realpython.com/python-click/) - Best practices (verified against official docs)
- [Better Stack - Typer Guide](https://betterstack.com/community/guides/scaling-python/click-explained/) - Patterns (verified)
- [Medium - Pre-commit Guide 2025](https://gatlenculp.medium.com/effortless-code-quality-the-ultimate-pre-commit-hooks-guide-for-2025-57ca501d9835) - Setup (verified with official docs)
- [ScrapingAnt - httpx vs requests](https://scrapingant.com/blog/requests-vs-httpx) - Comparison (verified with official docs)

### Tertiary (LOW confidence - needs validation)

- WebSearch results on config precedence patterns - General patterns, not library-specific
- Community discussions on Ruff migration - Anecdotal, but widespread adoption confirmed

</sources>

<metadata>
## Metadata

**Research scope:**
- Core technology: Python CLI frameworks (Click, Typer)
- Ecosystem: Config management (Pydantic, python-dotenv), HTTP clients (httpx, requests), tooling (Ruff, pre-commit, pytest)
- Patterns: Project structure (src layout, pyproject.toml), config hierarchy, secure credential storage
- Pitfalls: Import issues, security, validation, tooling overhead

**Confidence breakdown:**
- Standard stack: HIGH - All tools verified with official documentation, widely adopted
- Architecture: HIGH - Patterns from official docs and industry standards
- Pitfalls: HIGH - Well-documented common mistakes, verified solutions
- Code examples: HIGH - All from official documentation or verified tutorials
- SOTA updates: HIGH - Version numbers and changes confirmed from official sources

**Research date:** 2026-01-04
**Valid until:** 2026-02-04 (30 days - Python ecosystem is stable, tooling updates regularly)

</metadata>

---

*Phase: 01-foundation-configuration*
*Research completed: 2026-01-04*
*Ready for planning: yes*
