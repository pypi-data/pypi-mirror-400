"""Minimal quickstart script showing environment-driven logging configuration."""

from __future__ import annotations

import logging
import os

import logging_blueprint


def main() -> None:
    """Configure logging from env vars and emit a few illustrative messages."""
    os.environ.setdefault("PY_LOG", "info,example.basic=debug")
    os.environ.setdefault("PY_LOG_STYLE", "pretty")

    logging_blueprint.apply_env_logging()

    logger = logging.getLogger("example.basic")
    logger.debug("Loaded configuration from environment", extra={"config_source": "env"})
    logger.info("Service ready", extra={"port": 8080, "release": "2025.01.0"})
    logger.warning("Background job backlog increasing", extra={"pending_jobs": 17})
    logger.error("Transient dependency failure", extra={"service": "billing", "status_code": 502})


if __name__ == "__main__":
    main()
