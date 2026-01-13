"""Infralens CLI entry point."""

import sys

from infralens.config import load_env, ENV_FILE, CONFIG_DIR


def main():
    """Main entry point for infralens command."""
    load_env()

    args = sys.argv[1:]

    if args and args[0] == "setup":
        run_setup()
    elif args and args[0] == "fetch":
        run_fetch()
    else:
        # First run - if no config directory exists, launch setup wizard
        if not CONFIG_DIR.exists() or not ENV_FILE.exists():
            run_setup()
        else:
            # Launch TUI
            from infralens.app import InfralensApp
            app = InfralensApp()
            app.run()


def run_setup():
    """Launch the setup wizard."""
    from infralens.setup import SetupApp
    app = SetupApp()
    app.run()


def run_fetch():
    """Run the data fetcher."""
    # Import here to avoid loading fetch module unless needed
    from infralens import fetch
    fetch.fetch_all()


if __name__ == "__main__":
    main()
