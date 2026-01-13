"""Minimal ASGI-style app demonstrating logging-blueprint in an async context."""

from __future__ import annotations

import asyncio
import logging
import os
from collections.abc import Awaitable, Callable
from typing import Any

import logging_blueprint

logger = logging.getLogger("example.asgi")

ASGIReceive = Callable[[], Awaitable[dict[str, Any]]]
ASGISend = Callable[[dict[str, Any]], Awaitable[None]]


def configure_logging() -> None:
    """Apply env-driven logging with defaults tuned for ASGI output."""
    os.environ.setdefault("PY_LOG", "info,example.asgi=debug")
    os.environ.setdefault("PY_LOG_STYLE", "pretty")
    os.environ.setdefault("PY_LOG_STREAM", "stderr")
    logging_blueprint.apply_env_logging()


async def app(scope: dict[str, Any], receive: ASGIReceive, send: ASGISend) -> None:
    """Tiny ASGI application that logs request lifecycle events."""
    request_id = _get_header(scope, b"x-request-id") or "demo"
    path = scope.get("path", "/")
    method = scope.get("method", "GET")

    logger.info("request.start", extra={"path": path, "method": method, "request_id": request_id})

    body = b""
    while True:
        message = await receive()
        if message["type"] != "http.request":
            continue
        body += message.get("body", b"")
        if not message.get("more_body"):
            break

    if b"fail" in body:
        status = 500
        logger.error("request.failed", extra={"path": path, "request_id": request_id, "bytes_in": len(body)})
    else:
        status = 200
        logger.info("request.ok", extra={"path": path, "request_id": request_id, "bytes_in": len(body)})

    await send({"type": "http.response.start", "status": status, "headers": [(b"content-type", b"application/json")]})
    await send({"type": "http.response.body", "body": b'{"ok": true}'})
    logger.debug("response.sent", extra={"path": path, "status": status, "request_id": request_id})


def _get_header(scope: dict[str, Any], key: bytes) -> str | None:
    headers: list[tuple[bytes, bytes]] = scope.get("headers", [])
    for k, v in headers:
        if k == key:
            return v.decode("utf-8")
    return None


async def replay_request(method: str, path: str, body: bytes, request_id: str) -> None:
    """Invoke the ASGI app with a simulated HTTP request and print send() calls."""
    scope = {
        "type": "http",
        "http_version": "1.1",
        "method": method,
        "path": path,
        "headers": [
            (b"host", b"demo.local"),
            (b"x-request-id", request_id.encode("utf-8")),
            (b"content-length", str(len(body)).encode("utf-8")),
        ],
    }

    messages: list[dict[str, Any]] = [{"type": "http.request", "body": body, "more_body": False}]

    async def receive() -> dict[str, Any]:
        if messages:
            return messages.pop(0)
        return {"type": "http.disconnect"}

    async def send(message: dict[str, Any]) -> None:
        if message["type"] == "http.response.start":
            print(f"→ response {message['status']} for {path} ({request_id})")
        elif message["type"] == "http.response.body":
            payload = message.get("body", b"")
            print(f"   payload: {payload.decode('utf-8')}")

    await app(scope, receive, send)


async def main() -> None:
    """Run a couple of sample requests through the ASGI app."""
    configure_logging()
    await replay_request("GET", "/health", b"", "req-100")
    await replay_request("POST", "/ingest", b'{"events": 3}', "req-101")
    await replay_request("POST", "/ingest", b"fail", "req-102")


if __name__ == "__main__":
    asyncio.run(main())
