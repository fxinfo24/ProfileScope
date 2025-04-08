#!/usr/bin/env python3
"""
ProfileScope Main Entry Point
Starts either the web interface or the desktop application
"""

import argparse
import sys
import os


def main():
    """Main entry point for the application"""
    parser = argparse.ArgumentParser(
        description="ProfileScope: Social Media Profile Analysis Tool"
    )
    parser.add_argument(
        "--web", action="store_true", help="Run web interface (default)"
    )
    parser.add_argument(
        "--desktop", action="store_true", help="Run desktop application"
    )
    parser.add_argument("--host", default="127.0.0.1", help="Web interface host")
    parser.add_argument("--port", type=int, default=5000, help="Web interface port")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")

    args = parser.parse_args()

    # Default to web interface if no option specified
    if not args.desktop and not args.web:
        args.web = True

    if args.web:
        # Run the web interface
        print(f"Starting ProfileScope web interface on {args.host}:{args.port}")
        from app.web.app import create_app

        app = create_app()
        app.run(host=args.host, port=args.port, debug=args.debug)

    elif args.desktop:
        # Run the desktop application
        print("Starting ProfileScope desktop application")
        from app.desktop.app import main as run_desktop

        run_desktop()


if __name__ == "__main__":
    # Add the project root to Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    main()
