# Clacks GNU middleware

Lightweight FastAPI/Starlette middleware that keeps the tradition alive by adding the `X-Clacks-Overhead` HTTP header. Incoming headers are preserved, defaults can be configured, and duplicates are removed case-insensitively.

## What it does
- Adds `X-Clacks-Overhead` to every response, prefixed with `GNU` and joined by commas.
- Merges incoming request names, your configured defaults, and any names already set on the response.
- Deduplicates names case-insensitively to avoid repeated entries.
- Simple configuration via a shared `clacks_config` object.

## Install
```bash
pip install clacks-gnu-middleware
```

For local development:
```bash
pip install -e .
pip install -r requirements.txt  # tooling & test extras
```

## Quick start (FastAPI)
```python
from fastapi import FastAPI
from clacks_gnu_middleware.clacks_middleware import clacks_middleware, clacks_config

app = FastAPI()

# Optional: customize defaults before registering the middleware
clacks_config.default_names.extend([
    "Ada Lovelace",
    "Alan Turing",
])

app.middleware("http")(clacks_middleware)

@app.get("/ping")
async def ping():
    return {"status": "ok"}

# Run with: uvicorn app.application:app --reload
```

## Header behavior
- Header name: `X-Clacks-Overhead`.
- Values are emitted as `GNU <name>`, joined with commas.
- Order: configured defaults → incoming header values → names already set on the response.
- Names are deduplicated (case-insensitive). Empty or non-`GNU` values are ignored.

## Testing
```bash
pytest
```

## Notes
- The middleware uses a module-level `clacks_config`; set defaults before registering the middleware to avoid runtime mutation.
- License: GPL-3.0 (see LICENSE).
