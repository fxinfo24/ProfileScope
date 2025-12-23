"""
ProfileScope - Social Media Profile Analysis Tool
Core package initialization
"""

__version__ = "1.0.0"
__author__ = "ProfileScope Team"


def main() -> int:
    """Console entry point for the installed `profilescope` command.

    Why this exists:
    - `bin/run.py` is the repo's launcher script, but `bin/` is not a Python
      package (and we intentionally avoid adding new files like `bin/__init__.py`).
    - Packaging via `setup.py` requires an importable module path.

    This function mirrors the behavior of `bin/run.py`.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="ProfileScope: Social Media Profile Analysis Tool"
    )
    parser.add_argument("--web", action="store_true", help="Run web interface")
    parser.add_argument(
        "--desktop", action="store_true", help="Run desktop application (default)"
    )
    parser.add_argument("--host", default="127.0.0.1", help="Web interface host")
    parser.add_argument("--port", type=int, default=5000, help="Web interface port")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")

    args = parser.parse_args()

    # Default to desktop app if no option specified
    if not args.desktop and not args.web:
        args.desktop = True

    if args.desktop:
        print("Starting ProfileScope desktop application")
        from app.desktop.app import main as desktop_main

        return int(desktop_main() or 0)

    print(f"Starting ProfileScope web interface on {args.host}:{args.port}")
    from app.web.app import create_app

    flask_app = create_app()
    flask_app.run(host=args.host, port=args.port, debug=args.debug)
    return 0

