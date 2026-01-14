"""CLI entry point for nsys tool."""

from __future__ import annotations

import argparse
import json
import sys

from . import check_nsys, parse_nsys_report


def main():
    """CLI entry point for nsys tool."""
    parser = argparse.ArgumentParser(description="NSYS Tool")
    subparsers = parser.add_subparsers(dest="command")
    
    subparsers.add_parser("check", help="Check if NSYS is installed")
    
    parse_parser = subparsers.add_parser("parse", help="Parse .nsys-rep file")
    parse_parser.add_argument("file", help="Path to .nsys-rep file")
    parse_parser.add_argument("--output-dir", "-o", help="Output directory")
    
    args = parser.parse_args()
    
    if args.command == "check":
        result = check_nsys()
    elif args.command == "parse":
        result = parse_nsys_report(args.file, args.output_dir)
    else:
        parser.print_help()
        sys.exit(1)
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
