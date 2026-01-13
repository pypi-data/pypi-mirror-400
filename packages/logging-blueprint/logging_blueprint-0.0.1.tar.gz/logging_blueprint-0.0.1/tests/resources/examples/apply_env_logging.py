from __future__ import annotations

import logging

from logging_blueprint.conf import apply_env_logging


def main() -> None:
    apply_env_logging()

    logger = logging.getLogger("demo")
    logger.info("hello world", extra={"request_id": "abc123"})
    logger.error("boom", extra={"user_id": 42})


if __name__ == "__main__":
    main()
