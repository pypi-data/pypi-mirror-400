import pathlib
import sys

import pytest
from fastapi import FastAPI, Response
from fastapi.testclient import TestClient

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from clacks_gnu_middleware.clacks_middleware import (  # noqa: E402
    HEADER_NAME,
    clacks_config,
    clacks_middleware,
    parse_clacks_header,
)


@pytest.fixture(autouse=True)
def reset_config():
    defaults = list(clacks_config.default_names)
    flag = clacks_config.always_include_defaults
    clacks_config.default_names = ["Terry Pratchett"]
    clacks_config.always_include_defaults = True
    yield
    clacks_config.default_names = defaults
    clacks_config.always_include_defaults = flag


def build_app():
    app = FastAPI()
    app.middleware("http")(clacks_middleware)
    return app


def test_parse_clacks_header_filters_and_strips():
    raw = "GNU Terry Pratchett, Ada Lovelace, gnu  Alan Turing , , GNU  "
    assert parse_clacks_header(raw) == ["Terry Pratchett", "Alan Turing"]


def test_middleware_merges_and_dedupes():
    app = build_app()

    @app.get("/with-header")
    async def with_header():
        response = Response(content="ok")
        response.headers[HEADER_NAME] = "GNU Alan Turing"
        return response

    client = TestClient(app)
    resp = client.get(
        "/with-header",
        headers={HEADER_NAME: "GNU Ada Lovelace, GNU terry pratchett"},
    )
    assert resp.headers[HEADER_NAME] == (
        "GNU Terry Pratchett, GNU Ada Lovelace, GNU Alan Turing"
    )


def test_middleware_respects_disabled_defaults():
    clacks_config.always_include_defaults = False
    clacks_config.default_names = ["Terry Pratchett"]
    app = build_app()

    @app.get("/no-defaults")
    async def no_defaults():
        return {"ok": True}

    client = TestClient(app)
    resp = client.get("/no-defaults")
    assert HEADER_NAME not in resp.headers
