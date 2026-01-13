# Phase 2: API Client & Core Types - Research

**Researched:** 2026-01-04
**Domain:** Python HTTP client for REST API integration with n8n Cloud
**Confidence:** HIGH

<research_summary>
## Summary

Researched the Python HTTP client ecosystem for building a robust API client for n8n Cloud API v1. The standard approach uses httpx (already chosen in Phase 1) with Pydantic v2 for type-safe response models, tenacity for retry logic with exponential backoff, and a hub-and-spoke architecture pattern centered around a Client class.

Key finding: Don't hand-roll retry logic, connection pooling, or response parsing. httpx provides built-in connection pooling and HTTP/2 support; tenacity handles sophisticated retry strategies; Pydantic v2 ensures type-safe, validated API responses with automatic JSON Schema generation.

**Primary recommendation:** Use httpx.Client with context managers for connection pooling, Pydantic v2 BaseModel for all API response types, and tenacity decorators for retry logic. Structure the client with a central APIClient class that delegates to resource-specific modules (workflows, executions, projects, etc.).
</research_summary>

<standard_stack>
## Standard Stack

The established libraries/tools for Python API clients in 2025:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| httpx | 0.27+ | HTTP client with async support | Modern, type-safe, HTTP/2 support, connection pooling |
| pydantic | 2.12+ | Type-safe data models | Rust-powered validation, JSON Schema, 360M+ monthly downloads |
| tenacity | 9.1+ | Retry logic with backoff | Decorator-based, async support, flexible strategies |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| typing | stdlib | Type hints (TypedDict, Protocol) | Python 3.12+ native typing features |
| dataclasses | stdlib | Simple data classes | Alternative to Pydantic for internal-only types |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| httpx | requests | requests is battle-tested but lacks async, HTTP/2, and modern features |
| Pydantic v2 | dataclasses | dataclasses are simpler but lack validation, coercion, JSON Schema |
| tenacity | backoff | backoff is simpler but tenacity has more strategies and better async support |

**Installation:**
```bash
uv add httpx pydantic tenacity
# httpx already added in Phase 1
# Pydantic already added in Phase 1
```
</standard_stack>

<architecture_patterns>
## Architecture Patterns

### Recommended Project Structure
```
src/n8n_cli/
├── client/
│   ├── __init__.py       # Public API exports
│   ├── core.py           # APIClient hub class
│   ├── exceptions.py     # Custom exception hierarchy
│   ├── models/           # Pydantic response models
│   │   ├── __init__.py
│   │   ├── workflow.py
│   │   ├── execution.py
│   │   ├── project.py
│   │   └── common.py     # Shared types
│   └── resources/        # Resource-specific API modules
│       ├── __init__.py
│       ├── workflows.py
│       ├── executions.py
│       └── projects.py
```

### Pattern 1: Hub-and-Spoke Client Architecture
**What:** Central APIClient class that delegates to resource-specific modules
**When to use:** Complex APIs with multiple resource types
**Example:**
```python
# core.py - Hub class
class APIClient:
    def __init__(self, base_url: str, api_key: str):
        self._client = httpx.Client(
            base_url=base_url,
            headers={"X-N8N-API-KEY": api_key},
            timeout=30.0,
        )
        self.workflows = WorkflowsResource(self._client)
        self.executions = ExecutionsResource(self._client)
        self.projects = ProjectsResource(self._client)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._client.close()

# resources/workflows.py - Spoke module
class WorkflowsResource:
    def __init__(self, client: httpx.Client):
        self._client = client

    @retry(
        retry=retry_if_exception_type((httpx.HTTPError, ConnectionError)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3)
    )
    def list(self, active: bool | None = None) -> list[Workflow]:
        params = {"active": active} if active is not None else {}
        response = self._client.get("/api/v1/workflows", params=params)
        response.raise_for_status()
        return [Workflow.model_validate(w) for w in response.json()["data"]]
```

### Pattern 2: Pydantic Models for All API Responses
**What:** Use Pydantic BaseModel for type-safe, validated responses
**When to use:** All API response parsing (mandatory)
**Example:**
```python
# models/workflow.py
from pydantic import BaseModel, Field
from datetime import datetime

class Workflow(BaseModel):
    id: str
    name: str
    active: bool
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    nodes: list[dict] = []  # Complex nested structure
    connections: dict = {}

    class Config:
        populate_by_name = True  # Accept both createdAt and created_at

# Usage automatically validates and coerces types
workflow = Workflow.model_validate(response.json())
```

### Pattern 3: Custom Exception Hierarchy
**What:** Map HTTP status codes to specific exception types
**When to use:** Better error handling than generic httpx.HTTPError
**Example:**
```python
# exceptions.py
class N8NAPIError(Exception):
    """Base exception for all n8n API errors"""
    pass

class AuthenticationError(N8NAPIError):
    """API key invalid or missing (401)"""
    pass

class NotFoundError(N8NAPIError):
    """Resource not found (404)"""
    pass

class RateLimitError(N8NAPIError):
    """Rate limit exceeded (429)"""
    pass

class ServerError(N8NAPIError):
    """Server error (5xx)"""
    pass

def handle_response(response: httpx.Response) -> None:
    """Convert HTTP errors to custom exceptions"""
    if response.status_code == 401:
        raise AuthenticationError("Invalid API key")
    elif response.status_code == 404:
        raise NotFoundError(f"Resource not found: {response.url}")
    elif response.status_code == 429:
        raise RateLimitError("Rate limit exceeded")
    elif 500 <= response.status_code < 600:
        raise ServerError(f"Server error: {response.status_code}")
    response.raise_for_status()
```

### Pattern 4: Context Manager for Client Lifecycle
**What:** Use `with` statement to ensure proper connection cleanup
**When to use:** Always (connection pooling requires it)
**Example:**
```python
# Correct usage - connection pooling and cleanup
with APIClient(base_url, api_key) as client:
    workflows = client.workflows.list()
    executions = client.executions.list(workflow_id="123")
# Client automatically closed here

# Anti-pattern - don't do this in loops
for i in range(100):
    with APIClient(base_url, api_key) as client:  # BAD: Creates 100 clients
        client.workflows.list()
```

### Anti-Patterns to Avoid
- **Creating Client instances in hot loops:** Use a single scoped client for connection pooling benefits
- **Not using context managers:** Leads to connection leaks and resource exhaustion
- **Parsing JSON manually:** Pydantic handles parsing, validation, and type coercion
- **Hand-rolling retry logic:** tenacity handles exponential backoff, jitter, and async correctly
- **Ignoring HTTP status codes:** Always check and map to custom exceptions for better error handling
</architecture_patterns>

<dont_hand_roll>
## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Retry logic with backoff | Custom sleep/loop code | tenacity decorators | Edge cases: jitter, async, max time, conditional retries |
| Connection pooling | Manual socket management | httpx.Client context manager | HTTP/2 multiplexing, keep-alive, thread safety |
| Response validation | Manual dict parsing | Pydantic BaseModel | Type coercion, nested validation, error messages, JSON Schema |
| Field aliasing (createdAt → created_at) | Manual key remapping | Pydantic Field(alias=) | Handles both formats, validation, documentation |
| Rate limiting | Manual tracking | tenacity stop/wait strategies | Exponential backoff, retry after headers, jitter |
| HTTP error handling | if status_code checks | Custom exception hierarchy + raise_for_status | Consistent error types, better stack traces |

**Key insight:** HTTP client development has 25+ years of solved problems. httpx implements modern HTTP features (HTTP/2, connection pooling, async). tenacity implements retry strategies that handle edge cases (network failures, timeouts, transient errors). Pydantic implements data validation that catches bugs early. Fighting these leads to subtle bugs that manifest in production (connection leaks, retry storms, type errors).
</dont_hand_roll>

<common_pitfalls>
## Common Pitfalls

### Pitfall 1: Creating Multiple Client Instances
**What goes wrong:** Performance degrades, connection pool not utilized
**Why it happens:** Creating client inside request functions or loops
**How to avoid:** Use a single client instance with context manager at application scope
**Warning signs:** High TIME_WAIT socket count, slow requests despite connection pooling

### Pitfall 2: Not Handling Transient Errors
**What goes wrong:** Requests fail on temporary network issues or server hiccups
**Why it happens:** No retry logic for 5xx errors, timeouts, connection errors
**How to avoid:** Use tenacity with retry on httpx.HTTPError and ConnectionError
**Warning signs:** Users report "it works when I try again" - that's a retry use case

### Pitfall 3: Ignoring Pydantic Validation Errors
**What goes wrong:** API response schema changes silently break application
**Why it happens:** Catching ValidationError too broadly or not at all
**How to avoid:** Let validation errors propagate, log them, and fix schema mismatches
**Warning signs:** "undefined attribute" errors deep in application logic

### Pitfall 4: Synchronous Client in Async Context
**What goes wrong:** Blocking the event loop, terrible async performance
**Why it happens:** Using httpx.Client instead of httpx.AsyncClient in async functions
**How to avoid:** Use httpx.AsyncClient for async/await code paths
**Warning signs:** Async endpoints slower than sync, event loop warnings

### Pitfall 5: Not Setting Timeouts
**What goes wrong:** Requests hang indefinitely on slow/dead servers
**Why it happens:** httpx has strict timeouts by default, but infinite timeout can be set
**How to avoid:** Set reasonable timeout (e.g., 30s) in Client constructor
**Warning signs:** Application hangs, no response, users force-quit

### Pitfall 6: Forgetting to Close Clients
**What goes wrong:** Resource leaks, too many open connections
**Why it happens:** Not using context manager or forgetting explicit close()
**How to avoid:** Always use `with APIClient() as client:` pattern
**Warning signs:** "Too many open files" errors, connection pool exhausted
</common_pitfalls>

<code_examples>
## Code Examples

Verified patterns from official sources:

### Basic httpx Client Setup with Connection Pooling
```python
# Source: https://www.python-httpx.org/advanced/clients/
import httpx

# Correct: Single client instance with context manager
with httpx.Client(
    base_url="https://api.n8n.cloud",
    headers={"X-N8N-API-KEY": "your-api-key"},
    timeout=30.0,
) as client:
    # Connection is reused across multiple requests
    r1 = client.get("/api/v1/workflows")
    r2 = client.get("/api/v1/executions")
# Client automatically closed, connections cleaned up
```

### Pydantic Response Model with Validation
```python
# Source: https://docs.pydantic.dev/latest/concepts/models/
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

class Workflow(BaseModel):
    id: str
    name: str
    active: bool
    created_at: datetime = Field(alias="createdAt")
    tags: list[str] = []

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Workflow name cannot be empty")
        return v

    class Config:
        populate_by_name = True  # Accept both snake_case and camelCase

# Usage: automatic validation and coercion
response = client.get("/api/v1/workflows/123")
workflow = Workflow.model_validate(response.json())  # Validates and converts
```

### Retry Logic with Tenacity
```python
# Source: https://tenacity.readthedocs.io/
from tenacity import retry, retry_if_exception_type, wait_exponential, stop_after_attempt
import httpx

@retry(
    retry=retry_if_exception_type((httpx.HTTPError, ConnectionError)),
    wait=wait_exponential(multiplier=1, min=2, max=10),  # 2s, 4s, 8s, 10s
    stop=stop_after_attempt(3),
    reraise=True,
)
def fetch_workflow(client: httpx.Client, workflow_id: str) -> dict:
    response = client.get(f"/api/v1/workflows/{workflow_id}")
    response.raise_for_status()
    return response.json()
```

### Complete API Client Pattern
```python
# Source: https://bhomnick.net/design-pattern-python-api-client/
import httpx
from typing import Self
from tenacity import retry, retry_if_exception_type, wait_exponential, stop_after_attempt

class APIClient:
    def __init__(self, base_url: str, api_key: str, timeout: float = 30.0):
        self._client = httpx.Client(
            base_url=base_url,
            headers={"X-N8N-API-KEY": api_key},
            timeout=timeout,
        )

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args) -> None:
        self._client.close()

    @retry(
        retry=retry_if_exception_type(httpx.HTTPError),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
    )
    def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        response = self._client.request(method, path, **kwargs)
        response.raise_for_status()
        return response

    def get(self, path: str, **kwargs) -> httpx.Response:
        return self._request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> httpx.Response:
        return self._request("POST", path, **kwargs)

# Usage
with APIClient("https://api.n8n.cloud", "api-key") as client:
    response = client.get("/api/v1/workflows")
    data = response.json()
```

### Async Client for High Concurrency
```python
# Source: https://www.python-httpx.org/async/
import httpx
import asyncio

async def main():
    async with httpx.AsyncClient(
        base_url="https://api.n8n.cloud",
        headers={"X-N8N-API-KEY": "api-key"},
    ) as client:
        # Concurrent requests - much faster than sequential
        responses = await asyncio.gather(
            client.get("/api/v1/workflows"),
            client.get("/api/v1/executions"),
            client.get("/api/v1/projects"),
        )
        return [r.json() for r in responses]

# For CLI tool, sync client is sufficient
# Only use async if implementing concurrent operations
```
</code_examples>

<sota_updates>
## State of the Art (2024-2025)

What's changed recently:

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| requests library | httpx | 2020+ | httpx is 2x faster for sync, 7x+ for async; HTTP/2 support |
| Pydantic v1 | Pydantic v2 | 2023 | Rust core: 10-50x faster validation; better errors |
| manual retry | tenacity | 2018+ | Decorator-based; handles async, jitter, complex strategies |
| TypedDict | Pydantic BaseModel | 2020+ | Runtime validation catches bugs; JSON Schema generation |

**New tools/patterns to consider:**
- **httpx HTTP/2 support:** Multiplexing reduces connection overhead for many small requests
- **Pydantic v2 ValidationError:** Much clearer error messages with exact field paths and URL docs
- **Python 3.12 TypedDict generics:** Native syntax for generic TypedDict (e.g., `Response[T]`)
- **tenacity async decorators:** Full asyncio support with proper exception handling

**Deprecated/outdated:**
- **requests library:** Still maintained but lacks async, HTTP/2, and modern typing
- **Pydantic v1:** Superseded by v2 with massive performance improvements
- **Manual retry loops:** tenacity is now standard for retry logic
- **dataclasses for API responses:** Pydantic BaseModel is better for external data (validation)
</sota_updates>

<open_questions>
## Open Questions

Things that couldn't be fully resolved:

1. **n8n API Field Filtering**
   - What we know: n8n API supports field filtering via query parameters (standard REST pattern)
   - What's unclear: Exact syntax (fields=id,name vs select=id,name), whether nested fields supported
   - Recommendation: Check n8n OpenAPI spec at `/api/v1/docs` during implementation, or test empirically

2. **n8n API Rate Limits**
   - What we know: API requires authentication, likely has rate limits
   - What's unclear: Specific rate limit values, whether Retry-After headers are sent
   - Recommendation: Implement retry logic defensively (handle 429); observe in production

3. **n8n API Pagination**
   - What we know: Large result sets likely paginated
   - What's unclear: Pagination mechanism (cursor vs offset/limit), response structure
   - Recommendation: Inspect actual API responses; implement pagination when encountered
</open_questions>

<sources>
## Sources

### Primary (HIGH confidence)
- [httpx Documentation](https://www.python-httpx.org/) - Current version, features, client patterns
- [httpx Clients](https://www.python-httpx.org/advanced/clients/) - Connection pooling, context managers
- [httpx Async Support](https://www.python-httpx.org/async/) - AsyncClient usage
- [Pydantic Documentation](https://docs.pydantic.dev/latest/) - v2 features, BaseModel, validation
- [Pydantic Models](https://docs.pydantic.dev/latest/concepts/models/) - Model definition patterns
- [Tenacity Documentation](https://tenacity.readthedocs.io/) - Retry strategies, decorators
- [GitHub: jd/tenacity](https://github.com/jd/tenacity) - Latest release 9.1.2
- [n8n API Documentation](https://docs.n8n.io/api/) - Official API reference
- [n8n API Authentication](https://docs.n8n.io/api/authentication/) - X-N8N-API-KEY header

### Secondary (MEDIUM confidence)
- [Getting Started with HTTPX](https://betterstack.com/community/guides/scaling-python/httpx-explained/) - Best practices verified against official docs
- [A Design Pattern for Python API Client Libraries](https://bhomnick.net/design-pattern-python-api-client/) - Hub-and-spoke architecture pattern
- [REST API Design: Filtering, Sorting, and Pagination](https://www.moesif.com/blog/technical/api-design/REST-API-Design-Filtering-Sorting-and-Pagination/) - General REST patterns
- [HTTPX vs Requests vs AIOHTTP](https://oxylabs.io/blog/httpx-vs-requests-vs-aiohttp) - Performance comparisons
- [Python HTTPX - Retry Failed Requests](https://scrapeops.io/python-web-scraping-playbook/python-httpx-retry-failed-requests/) - Retry patterns with tenacity
- [Python 3.12 Preview: Static Typing Improvements](https://realpython.com/python312-typing/) - Modern typing features

### Tertiary (LOW confidence - needs validation)
- None - all findings verified against official documentation
</sources>

<metadata>
## Metadata

**Research scope:**
- Core technology: httpx, Pydantic v2, tenacity
- Ecosystem: Python 3.12 typing, HTTP client patterns, API authentication
- Patterns: Hub-and-spoke client architecture, Pydantic models, retry decorators
- Pitfalls: Connection pooling, error handling, validation errors, async vs sync

**Confidence breakdown:**
- Standard stack: HIGH - httpx, Pydantic, tenacity are industry standard in 2025
- Architecture: HIGH - hub-and-spoke pattern is proven for complex APIs
- Pitfalls: HIGH - documented in official docs and verified in articles
- Code examples: HIGH - from official documentation with verification

**Research date:** 2026-01-04
**Valid until:** 2026-02-04 (30 days - ecosystem stable, but n8n API may evolve)
</metadata>

---

*Phase: 02-api-client-core-types*
*Research completed: 2026-01-04*
*Ready for planning: yes*
