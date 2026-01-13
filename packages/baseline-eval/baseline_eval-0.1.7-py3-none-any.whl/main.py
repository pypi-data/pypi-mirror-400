"""Thin wrapper to preserve `python main.py` while delegating to package CLI."""

from baseline.cli import main

if __name__ == "__main__":
    main()
