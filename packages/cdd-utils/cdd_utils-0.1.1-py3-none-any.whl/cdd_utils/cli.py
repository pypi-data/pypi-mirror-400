#!/usr/bin/env python3
"""CDD Utils - CLI entry point."""

import argparse
import sys

from . import __version__
from .utf8_fix import utf8_main


def main():
    """Main CLI dispatcher."""
    parser = argparse.ArgumentParser(
        prog='cdd-utils',
        description='General utilities for AI-assisted development',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  utf8    UTF-8 corruption detection and ASCII normalization

Examples:
  cdd-utils utf8 --report src/
  cdd-utils utf8 --dry-run --smart src/main.py
  cdd-utils utf8 --smart-fix src/
        """
    )
    
    parser.add_argument(
        '--version', '-V',
        action='version',
        version=f'cdd-utils {__version__}'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # utf8 subcommand
    utf8_parser = subparsers.add_parser(
        'utf8',
        help='UTF-8 corruption detection and ASCII normalization',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modes:
  --report       Scan and report all non-ASCII
  --dry-run      Preview fixes line-by-line
  --fix          Normalize ALL non-ASCII to ASCII
  --smart-fix    Normalize only SUSPICIOUS non-ASCII

Smart mode (--dry-run --smart or --smart-fix) distinguishes:
  LEGITIMATE: Isolated non-ASCII (intentional symbols like • ↻ →)
  SUSPICIOUS: Clustered non-ASCII (likely corruption like ->)

Examples:
  cdd-utils utf8 --report src/              # Find all non-ASCII
  cdd-utils utf8 --dry-run file.py          # Preview all fixes
  cdd-utils utf8 --dry-run --smart file.py  # Categorize issues
  cdd-utils utf8 --smart-fix file.py        # Fix corruption only
  cdd-utils utf8 --fix src/ --ext .py .scd  # Fix all in .py/.scd files
        """
    )
    
    mode = utf8_parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--report', action='store_true',
                      help='Scan and report all non-ASCII')
    mode.add_argument('--dry-run', action='store_true',
                      help='Preview fixes line-by-line (no changes made)')
    mode.add_argument('--fix', action='store_true',
                      help='Normalize ALL non-ASCII to ASCII (backups created)')
    mode.add_argument('--smart-fix', action='store_true',
                      help='Normalize only SUSPICIOUS non-ASCII (backups created)')
    
    utf8_parser.add_argument('path', help='File or directory to process')
    utf8_parser.add_argument('--smart', action='store_true',
                             help='With --dry-run: categorize as legitimate vs suspicious')
    utf8_parser.add_argument('--ext', nargs='+', metavar='EXT',
                             help='File extensions to process (e.g., .scd .py)')
    utf8_parser.add_argument('--backup-dir', metavar='DIR',
                             help='Custom backup directory')
    utf8_parser.add_argument('-q', '--quiet', action='store_true',
                             help='Summary only')
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(0)
    
    if args.command == 'utf8':
        sys.exit(utf8_main(args))
    
    # Future commands would be added here
    parser.print_help()
    sys.exit(1)


if __name__ == '__main__':
    main()
