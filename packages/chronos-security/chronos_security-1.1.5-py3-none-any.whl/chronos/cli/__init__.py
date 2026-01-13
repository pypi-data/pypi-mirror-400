"""
CHRONOS CLI Module
==================

Command-line interface for the CHRONOS quantum security platform.
"""

# Lazy import to avoid circular imports
def _get_app():
    from chronos.cli.main import app
    return app

def _get_main():
    from chronos.cli.main import main
    return main

__all__ = ["app", "main"]

# For backwards compatibility, provide lazy access
def __getattr__(name):
    if name == "app":
        return _get_app()
    elif name == "main":
        return _get_main()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
