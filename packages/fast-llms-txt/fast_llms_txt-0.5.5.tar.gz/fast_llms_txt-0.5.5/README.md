# fast-llms-txt

[![PyPI version](https://img.shields.io/pypi/v/fast-llms-txt)](https://pypi.org/project/fast-llms-txt/)
[![Python](https://img.shields.io/pypi/pyversions/fast-llms-txt)](https://pypi.org/project/fast-llms-txt/)
[![License](https://img.shields.io/pypi/l/fast-llms-txt)](https://github.com/AlteredCraft/fast-llms-txt/blob/main/LICENSE)
[![codecov](https://codecov.io/github/AlteredCraft/fast-llms-txt/graph/badge.svg?token=PD0EADRRJP)](https://codecov.io/github/AlteredCraft/fast-llms-txt)

Generate an `llms.txt` markdown manifest from your FastAPI OpenAPI schema for AI agents. This results in a ~40-50% size reduction vs the output of a OpenAPI spec JSON.

Inspired by the [llms.txt specification](https://llmstxt.org/) for LLM-friendly documentation.

## Why?

OpenAPI and FastAPI's support for it are excellent, but the specification is designed for deterministic machine interpretation. It must be complete and precise. Every schema, every `$ref`, every possible response. This results in a very large document.

AI agents have different needs:

- **Context windows are limited.** A 50KB OpenAPI spec consumes tokens that could be used for reasoning.
- **Agents can infer.** A `Task` mentioned in one endpoint is probably the same `Task` concept elsewhere. They don't need every relationship spelled out.
- **Agents recover from errors.** If an API responds that `foo` needs to be an integer, the agent adapts. It doesn't need perfect type information upfront.

This project applies the [llms.txt](https://llmstxt.org/) philosophy, Concise, readable documentation for LLMs—to APIs.

## Installation

```bash
uv add fast-llms-txt
```

## Usage

```python
from fastapi import FastAPI
from fast_llms_txt import create_llms_txt_router

app = FastAPI(title="My API", description="A sample API")

@app.get("/users")
def list_users(limit: int = 10):
    """List all users."""
    return []

# Mount the llms.txt endpoint
app.include_router(create_llms_txt_router(app), prefix="/docs")
```

The `prefix` determines the final URL path. For example:
- `prefix="/docs"` → `GET /docs/llms.txt`
- `prefix="/api/v1/docs"` → `GET /api/v1/docs/llms.txt`

Now `GET /docs/llms.txt` returns:

```markdown
# My API

> A sample API

## Endpoints

### `GET /users` - List all users.

- **Request Parameters**:
  - `limit` (integer, optional)
- **Returns** (200): Successful Response
```

## API

### `create_llms_txt_router(app, path="/llms.txt")`

Creates a FastAPI router that serves the llms.txt endpoint.

- `app`: Your FastAPI application instance
- `path`: The endpoint path (default: `/llms.txt`)

### `generate_llms_txt(openapi_schema)`

Directly convert an OpenAPI schema dict to llms.txt markdown string.

---

## Appendix: Release Procedure

### Versioning

This project uses [semantic versioning](https://semver.org/):
- **PATCH** (0.1.x): Bug fixes, no API changes
- **MINOR** (0.x.0): New features, backward compatible
- **MAJOR** (x.0.0): Breaking API changes

### Prerequisites

- [GitHub CLI](https://cli.github.com/) installed and authenticated (`gh auth login`)

### Release Steps

Run the release script:
```bash
./scripts/release.sh 0.2.0
```

This will:
1. Update version in `pyproject.toml` and `fast_llms_txt/__init__.py`
2. Show diff and prompt for confirmation
3. Commit the version bump
4. Prompt for release notes (or auto-generate from commits)
5. Push and create GitHub release (triggers PyPI publish via GitHub Actions)

### Infrastructure

- **PyPI**: [pypi.org/project/fast-llms-txt](https://pypi.org/project/fast-llms-txt/)
- **Trusted Publishing**: No tokens required; GitHub Actions authenticates via OIDC
- **Environment**: `release` environment in GitHub repo settings restricts publishing to `v*` tags
