"""CLI for PintGlass unit configuration management."""

import argparse
import sys

from pint_glass.dimensions import export_dimensions


def main() -> None:
    """Main entry point for the pint-glass CLI."""
    parser = argparse.ArgumentParser(description="PintGlass CLI Utility")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Export command
    export_parser = subparsers.add_parser(
        "export", help="Export unit configuration to JSON"
    )
    export_parser.add_argument(
        "-o", "--output", help="Output file path (default: stdout)", default=None
    )

    args = parser.parse_args()

    if args.command == "export":
        try:
            result = export_dimensions(args.output)
            if not args.output:
                print(result)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
