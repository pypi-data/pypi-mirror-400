# Roadmap: n8n CLI

## Overview

A complete command-line tool for managing n8n Cloud workflows, starting with foundational configuration and authentication, building a robust API client, implementing comprehensive workflow and execution management commands, adding project and user management capabilities, enhancing developer experience with shell completion and utilities, and finishing with a quality test suite.

## Domain Expertise

None

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Foundation & Configuration** - Core infrastructure, auth, and configuration system (Complete: 2026-01-04)
- [x] **Phase 2: API Client & Core Types** - Robust API client with field filtering and data types (Complete: 2026-01-04)
- [x] **Phase 3: Workflow Management** - Full workflow commands (list, view, pull, push, create, delete, activate, deactivate, move, diff, open) (Complete: 2026-01-05)
- [x] **Phase 4: Execution Management** - Execution commands (list, view, download, retry) (Complete: 2026-01-05)
- [x] **Phase 5: Project & User Management** - Project, user, and member commands (Complete: 2026-01-05)
- [x] **Phase 6: Developer Experience** - Shell completion, progressive verbosity, utility functions (Complete: 2026-01-05)
- [x] **Phase 7: Quality & Testing** - Comprehensive test suite and pre-commit hooks (Complete: 2026-01-05)

## Phase Details

### Phase 1: Foundation & Configuration
**Goal**: Establish CLI framework with Click, implement configuration system for storing settings, and create authentication system for n8n Cloud API access
**Depends on**: Nothing (first phase)
**Research**: Likely (new project setup, technology choices)
**Research topics**: Click best practices for CLI apps, config file storage patterns (TOML vs JSON vs YAML), auth token management and secure storage, n8n API authentication flow
**Plans**: TBD

Plans:
- TBD (will be defined during phase planning)

### Phase 2: API Client & Core Types
**Goal**: Build robust HTTP client for n8n API with proper field filtering, error handling, and data type definitions
**Depends on**: Phase 1
**Research**: Complete (2026-01-04)
**Research topics**: n8n Cloud API v1 documentation, field filtering capabilities, HTTP client options (requests vs httpx vs others), API error handling patterns
**Plans**: 2 plans

Plans:
- [x] **Plan 1**: API Client Core Infrastructure - Exception hierarchy, APIClient hub class, retry logic (Complete: 2026-01-04)
- [x] **Plan 2**: Pydantic Response Models and Resources - Type-safe models and WorkflowsResource (Complete: 2026-01-04)

### Phase 3: Workflow Management
**Goal**: Implement complete workflow command suite including list, view, pull, push, create, delete, activate, deactivate, move, diff, open, and retry
**Depends on**: Phase 2
**Research**: Unlikely (builds on phase 2 patterns, CRUD operations)
**Plans**: 4 plans

Plans:
- [x] **Plan 1**: WorkflowsResource API Methods - Complete CRUD and utility methods (Complete: 2026-01-05)
- [x] **Plan 2**: Basic Workflow CLI Commands - list, view, activate, deactivate commands (Complete: 2026-01-05)
- [x] **Plan 3**: File Operation Commands - Utility functions and pull/push/create commands (Complete: 2026-01-05)
- [x] **Plan 4**: Advanced Workflow Commands - diff, delete, move (placeholder), open (Complete: 2026-01-05)

### Phase 4: Execution Management
**Goal**: Implement execution commands for listing, viewing, downloading, and retrying workflow executions with status filtering
**Depends on**: Phase 3
**Research**: Unlikely (similar patterns to workflow management)
**Plans**: 3 plans

Plans:
- [x] **Plan 1**: ExecutionsResource API Methods - list/get/retry methods with filtering (Complete: 2026-01-05)
- [x] **Plan 2**: List and View Commands - CLI commands for execution listing and viewing (Complete: 2026-01-04)
- [x] **Plan 3**: Download and Retry Commands - Download execution data and retry failed executions (Complete: 2026-01-05)

### Phase 5: Project & User Management
**Goal**: Implement project, user, and member management commands with role support
**Depends on**: Phase 4
**Research**: Unlikely (more API commands following established patterns)
**Plans**: 3 plans

Plans:
- [x] **Plan 1**: ProjectsResource and UsersResource API Methods - API methods for projects/users with retry logic (Complete: 2026-01-05)
- [x] **Plan 2**: Project and User CLI Commands - list, view, invite, remove commands (Complete: 2026-01-05)
- [x] **Plan 3**: Member Management Commands - Member list/add/remove API methods and CLI commands (Complete: 2026-01-05)

### Phase 6: Developer Experience
**Goal**: Add shell completion for workflows/projects/files, implement progressive verbosity (-v to -vvvv), and create utility functions for input resolution and file handling
**Depends on**: Phase 5
**Research**: Likely (shell completion implementation)
**Research topics**: Click shell completion implementation, progressive verbosity patterns, filename sanitization best practices
**Plans**: TBD

Plans:
- [x] **Plan 1**: Utility Functions - Project detection, directory management, and workflow saving (Complete: 2026-01-05)
- [x] **Plan 2**: Progressive Verbosity Standardization - Standardize all commands to use count=True (Complete: 2026-01-05)
- [x] **Plan 3**: Shell Completion - Dynamic completion for workflows, projects, and files (Complete: 2026-01-05)

### Phase 7: Quality & Testing
**Goal**: Build comprehensive test suite with minimal mocking and duplication, configure pre-commit hooks for code quality
**Depends on**: Phase 6
**Research**: Complete (2026-01-05)
**Plans**: 1 plan

Plans:
- [x] **Plan 1**: Test Coverage Improvements - Improve coverage from 84% to 88%, fix test performance (Complete: 2026-01-05)

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6 → 7

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation & Configuration | 2/2 | Complete | 2026-01-04 |
| 2. API Client & Core Types | 2/2 | Complete | 2026-01-04 |
| 3. Workflow Management | 4/4 | Complete | 2026-01-05 |
| 4. Execution Management | 3/3 | Complete | 2026-01-05 |
| 5. Project & User Management | 3/3 | Complete | 2026-01-05 |
| 6. Developer Experience | 3/3 | Complete | 2026-01-05 |
| 7. Quality & Testing | 1/1 | Complete | 2026-01-05 |
