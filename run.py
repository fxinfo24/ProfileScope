#!/usr/bin/env python3
import argparse
import sys
import os
import logging

def main():
    parser = argparse.ArgumentParser(description="SocialInsight: Social Media Profile Analyzer")
    parser.add_argument("--mode", choices=["desktop", "web"], default="desktop",
                      help="Run mode: desktop or web application")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--port", type=int, default=5000, help="Port for web server")
    parser.add_argument("--config", help="Path to configuration file")
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the selected application mode
    if args.mode == "desktop":
        from app.desktop.app import AnalyzerApp
        app = AnalyzerApp(config_path=args.config)
        app.mainloop()
    elif args.mode == "web":
        from app.web.app import app as flask_app
        flask_app.run(host='0.0.0.0', port=args.port, debug=args.debug)
    else:
        print(f"Unknown mode: {args.mode}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
