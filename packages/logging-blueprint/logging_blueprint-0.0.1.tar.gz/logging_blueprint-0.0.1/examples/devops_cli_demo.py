"""Simulated DevOps CLI that mixes stdout output with structured logging."""

from __future__ import annotations

import logging
import os
from collections.abc import Iterable

import logging_blueprint


def configure_logging() -> logging.Logger:
    """Apply env-driven logging with sensible defaults for the demo."""
    os.environ.setdefault("PY_LOG", "info,example.devops=debug")
    os.environ.setdefault("PY_LOG_STYLE", "pretty")
    os.environ.setdefault("PY_LOG_STREAM", "stderr")

    logging_blueprint.apply_env_logging()
    return logging.getLogger("example.devops")


def run_step(step_name: str, logger: logging.Logger) -> None:
    """Emit stdout progress plus logging records to mirror a CLI workflow."""
    logger.info("Starting step", extra={"step": step_name})
    print(f"$ {step_name}")

    for progress in (25, 50, 75):
        print(f"{step_name}: {progress}% complete")
        logger.debug("Progress update", extra={"step": step_name, "progress_pct": progress})

    if step_name == "migrate-db":
        logger.warning("Migration running in dry-run mode", extra={"step": step_name, "target": "tenant_prod"})
        print("dry-run: SQL applied to shadow schema only")

    logger.info("Step finished", extra={"step": step_name, "duration_ms": 3200})
    print()


def emit_summary(logger: logging.Logger, incidents: Iterable[str]) -> None:
    """Summarize the release with a short incident list."""
    for incident in incidents:
        logger.error("Detected issue during release", extra={"incident": incident})
    logger.info("Deployment completed", extra={"result": "success", "duration": "6m14s"})
    print("Release complete. See logs for details.")


def main() -> None:
    """Run the faux deployment workflow."""
    logger = configure_logging()

    for step in ("build-artifacts", "deploy-api", "migrate-db"):
        run_step(step, logger)

    emit_summary(logger, incidents=("api-healthcheck latency spike",))


if __name__ == "__main__":
    main()
