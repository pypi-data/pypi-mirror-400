"""
CLI for pyPASreporter.
"""

import argparse
import sys
from pathlib import Path

from . import __version__
from .core import load_evd, load_pacli


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="pypasreporter",
        description="CyberArk PAM reporting and analytics toolkit",
    )
    parser.add_argument(
        "--version", "-V", action="version", version=f"%(prog)s {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # load-evd command
    evd_parser = subparsers.add_parser("load-evd", help="Load EVD export files")
    evd_parser.add_argument("source_dir", type=Path, help="Path to EVD exports directory")

    # load-pacli command
    pacli_parser = subparsers.add_parser("load-pacli", help="Load PACLI configuration files")
    pacli_parser.add_argument("source_dir", type=Path, help="Path to PACLI exports directory")

    args = parser.parse_args()

    if args.command == "load-evd":
        result = load_evd(args.source_dir)
        print(f"Loaded {len(result)} EVD files")
        for filename in result:
            print(f"  - {filename}")
        return 0

    elif args.command == "load-pacli":
        result = load_pacli(args.source_dir)
        print(f"Loaded {len(result)} PACLI files")
        for filename in result:
            print(f"  - {filename}")
        return 0

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
