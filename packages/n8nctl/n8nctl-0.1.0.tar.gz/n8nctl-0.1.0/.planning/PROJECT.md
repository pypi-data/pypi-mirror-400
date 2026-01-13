# n8n CLI

## What This Is

A command-line tool for managing n8n Cloud workflows, inspired by GitHub's `gh` CLI. Enables developers to list, view, and manage workflows from the terminal, pull workflows to local JSON files for version control, push local changes back to n8n cloud, compare local vs cloud versions (diff), and manage projects, users, and executions.

## Core Value

Complete workflow management from the terminal with a local-first editing experience. The full suite of workflow, execution, project, user, and member management commands working seamlessly together.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Configuration system with auth and config commands
- [ ] API client with proper field filtering for n8n API
- [ ] Workflow commands: list, view, pull, push, create, delete, activate, deactivate, move, diff, open, retry
- [ ] Execution commands: list, view, download, retry with status filtering
- [ ] Project commands: list, view with member display
- [ ] User commands: list, invite, remove
- [ ] Member commands: list, add, remove with role support
- [ ] Flexible input resolution (names, IDs, or file paths work interchangeably)
- [ ] Progressive verbosity (-v to -vvvv for increasing detail)
- [ ] Shell completion for workflows, projects, and file paths
- [ ] Utility functions: filename sanitization, workflow file finding, project detection
- [ ] Quality test suite with minimal mocking and duplication
- [ ] Pre-commit hooks for code quality

### Out of Scope

- Tags/credentials/variables management commands — API exists but no CLI commands needed for v1
- Source control integration beyond local file management — focus on manual pull/push workflow
- Custom workflow templates — use n8n UI for creation, CLI for management
- Workflow versioning beyond what n8n API provides — rely on git for local versioning
- Advanced execution filtering/querying — basic status filtering is sufficient

## Context

**Background:**
This is a reimplementation from scratch based on previous work. A comprehensive REQUIREMENTS.md document exists with complete specifications for all commands, API methods, project structure, testing approach, and code quality standards.

**Technical Environment:**
- Target: n8n Cloud API (v1)
- Primary use case: Terminal-based workflow management for developers
- Local-first workflow: pull to JSON files, edit locally, diff changes, push back

**Quality Focus:**
Emphasis on code quality over just test coverage. Tests should be high-quality with minimal mocking and minimal duplication, not just hitting coverage metrics.

## Constraints

- **Language**: Python 3.12+ — modern Python patterns and syntax
- **Tooling**: Flexible on specific choices, open to improvements over REQUIREMENTS.md suggestions
- **Core libraries**: Click for CLI framework, requests for HTTP client (or better alternatives)
- **Success criteria**: Daily usability + complete implementation + high code quality

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| _No decisions yet_ | _Will track as made during planning and implementation_ | — Pending |

---
*Last updated: 2026-01-04 after initialization*
