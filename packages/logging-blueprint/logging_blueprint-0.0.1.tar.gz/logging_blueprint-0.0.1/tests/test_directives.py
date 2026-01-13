"""Unit test for logging_blueprint/directives.py."""

from logging_blueprint.directives import parse_directives


def test_parse_directives_handles_defaults_and_modules() -> None:
    directives = parse_directives("debug,myapp.db=warn,myapp.api=error,INFO")

    assert directives.default_level_name == "INFO"
    assert directives.module_levels == (("myapp.db", "WARNING"), ("myapp.api", "ERROR"))
