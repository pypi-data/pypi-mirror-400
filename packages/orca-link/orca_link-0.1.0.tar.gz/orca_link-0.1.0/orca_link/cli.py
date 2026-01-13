"""
Command-line interface for OrcaLink
"""
import sys
from typing import Optional


def main(argv: Optional[list] = None) -> int:
    """
    Main entry point for OrcaLink CLI
    
    Args:
        argv: Command line arguments (defaults to sys.argv[1:])
    
    Returns:
        Exit code (0 for success)
    """
    if argv is None:
        argv = sys.argv[1:]
    
    # Parse arguments
    if not argv or argv[0] in ('hello', '--hello'):
        print("Hello, World! 🦑 Welcome to OrcaLink!")
        return 0
    elif argv[0] in ('--version', '-v'):
        from . import __version__
        print(f"OrcaLink {__version__}")
        return 0
    elif argv[0] in ('--help', '-h'):
        print_help()
        return 0
    else:
        print(f"Unknown command: {argv[0]}")
        print_help()
        return 1


def print_help() -> None:
    """Print help message"""
    help_text = """
OrcaLink - Orchestration and Linking for Distributed Systems

Usage:
    orca-link [COMMAND]

Commands:
    hello, --hello      Print hello world message
    --version, -v       Show version information
    --help, -h          Show this help message

Examples:
    orca-link hello
    orca-link --version
    orca-link --help
"""
    print(help_text)


if __name__ == '__main__':
    sys.exit(main())

