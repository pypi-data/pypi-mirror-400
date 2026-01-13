# Phase 1: Foundation & Configuration - Context

**Gathered:** 2026-01-04
**Status:** Ready for research

<vision>
## How This Should Work

Simple and developer-friendly: drop your n8n API key and instance URL into a `.env` file and start using the CLI. No wizards, no complex setup - just environment variables like any other developer tool.

Configuration should be flexible enough to support different workflows:
- Local `.env` file in your project directory for project-specific n8n instances
- Global config file in home directory (`~/.n8n-cli` or similar) for your default instance
- Local takes precedence when both exist

This is the foundation that everything else builds on - get authentication working and set up the project structure with quality tooling from the start.

</vision>

<essential>
## What Must Be Nailed

- **Working authentication** - API calls to n8n Cloud reliably authenticate with the provided credentials
- **Project structure with quality tooling** - Pre-commit hooks and code quality setup from day one, not bolted on later

</essential>

<boundaries>
## What's Out of Scope

- No actual API calls for workflows/executions - that's Phase 2 and beyond
- No fancy config UI or interactive wizards - just simple .env files
- No multi-account support or account switching - one API key at a time
- No config management commands (like `n8n-cli config set`) - direct file editing is fine

</boundaries>

<specifics>
## Specific Ideas

Follow standard Python CLI patterns - look at how other well-designed Python CLIs handle configuration and authentication. No need to reinvent anything here.

Standard .env format:
```
N8N_API_KEY=your-api-key-here
N8N_INSTANCE_URL=https://your-instance.app.n8n.cloud
```

</specifics>

<notes>
## Additional Context

This phase is about laying the groundwork right. Get authentication solid and project structure clean so we can move fast in later phases without accumulating technical debt.

</notes>

---

*Phase: 01-foundation-configuration*
*Context gathered: 2026-01-04*
