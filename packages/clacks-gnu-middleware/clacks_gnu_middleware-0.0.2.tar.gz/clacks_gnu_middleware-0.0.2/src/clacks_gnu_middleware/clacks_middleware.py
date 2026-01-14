from typing import Iterable
from fastapi import Request
from fastapi.responses import Response

HEADER_NAME = "X-Clacks-Overhead"

class ClacksConfig:
    """
    Configuration for X-Clacks-Overhead middleware.
    """

    def __init__(self,
                 default_names: Iterable[str] = ("Terry Pratchett",),
                 always_include_defaults: bool = True):
        self.default_names = list(default_names)
        self.always_include_defaults = always_include_defaults


# You can modify this instance in your main.py BEFORE the middleware loads.
clacks_config = ClacksConfig(
    default_names=[
        "Terry Pratchett",
        # Add any custom commemorations here:
        # "Ada Lovelace",
        # "Douglas Adams",
    ],
    always_include_defaults=True,
)


def parse_clacks_header(raw_value: str) -> list[str]:
    """
    Extract 'names' from 'GNU <name>' patterns.
    Supports comma-separated lists.
    """
    if not raw_value:
        return []

    names = []
    for part in raw_value.split(","):
        entry = part.strip()
        if entry.lower().startswith("gnu "):
            name = entry[4:].strip()
            if name:
                names.append(name)

    return names


async def clacks_middleware(request: Request, call_next):
    # ── 1. Extract incoming names ───────────────────────────────────────────
    incoming_raw = request.headers.get(HEADER_NAME, "")
    incoming_names = parse_clacks_header(incoming_raw)

    # ── 2. Storage for deduplication ───────────────────────────────────────
    names: list[str] = []
    seen = set()

    def add_name(n: str):
        n = n.strip()
        if not n:
            return
        key = n.lower()
        if key in seen:
            return
        seen.add(key)
        names.append(n)

    # ── 3. Add configured default names first (if enabled) ─────────────────
    if clacks_config.always_include_defaults:
        for dn in clacks_config.default_names:
            add_name(dn)

    # ── 4. Add incoming request names ───────────────────────────────────────
    for n in incoming_names:
        add_name(n)

    # ── 5. Process the request ─────────────────────────────────────────────
    response: Response = await call_next(request)

    # ── 6. Add any existing response names (if already set) ────────────────
    existing_raw = response.headers.get(HEADER_NAME, "")
    existing_names = parse_clacks_header(existing_raw)
    for n in existing_names:
        add_name(n)

    # ── 7. Write final header ──────────────────────────────────────────────
    if names:
        response.headers[HEADER_NAME] = ", ".join(f"GNU {n}" for n in names)

    return response



#EXAMPLE USAGE IN main.py:
#from fastapi import FastAPI
#from clacks_middleware import clacks_middleware, clacks_config

#app = FastAPI()

# Optional: add more names before starting
#clacks_config.default_names.append("Ada Lovelace")
#clacks_config.default_names.append("Alan Turing")

#app.middleware("http")(clacks_middleware)