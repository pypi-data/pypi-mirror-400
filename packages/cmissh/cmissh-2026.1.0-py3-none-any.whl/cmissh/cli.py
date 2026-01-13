"""
CMIS Shell - Command-line interface for CMIS repositories.
"""

import argparse
import sys

from cmissh.shell import CmisShell


def main():
    """Main entry point for the cmissh CLI."""
    parser = argparse.ArgumentParser(
        description="CMIS Shell - Interactive shell for CMIS repositories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  cmissh

  # Connect and enter interactive mode
  cmissh -u admin -p admin http://localhost:8080/alfresco/api/-default-/public/cmis/versions/1.1/atom

  # Execute a single command
  cmissh -u admin -p admin -e "ls" http://localhost:8080/alfresco/api/-default-/public/cmis/versions/1.1/atom

  # Execute commands from a file
  cmissh -u admin -p admin -b script.cmis http://localhost:8080/alfresco/api/-default-/public/cmis/versions/1.1/atom
        """,
    )

    parser.add_argument(
        "url",
        nargs="?",
        help="CMIS repository URL (can also be set with 'connect' command)",
    )

    parser.add_argument(
        "-u",
        "--username",
        help="Username for authentication",
    )

    parser.add_argument(
        "-p",
        "--password",
        help="Password for authentication",
    )

    parser.add_argument(
        "-e",
        "--execute",
        metavar="COMMAND",
        help="Execute a single command and exit",
    )

    parser.add_argument(
        "-b",
        "--batch",
        metavar="FILE",
        help="Execute commands from a file",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="cmissh 0.1.0",
    )

    args = parser.parse_args()

    # Create shell instance
    shell = CmisShell(verbose=args.verbose)

    # Auto-connect if URL is provided
    if args.url:
        username = args.username or "admin"
        password = args.password or "admin"
        try:
            shell.do_connect(f"{username}:{password}@{args.url}")
        except Exception as e:
            print(f"Error connecting to repository: {e}", file=sys.stderr)
            return 1

    # Execute single command mode
    if args.execute:
        try:
            shell.onecmd(args.execute)
            return 0
        except Exception as e:
            print(f"Error executing command: {e}", file=sys.stderr)
            return 1

    # Batch mode
    if args.batch:
        try:
            with open(args.batch) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        shell.onecmd(line)
            return 0
        except FileNotFoundError:
            print(f"Error: Batch file '{args.batch}' not found", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Error executing batch file: {e}", file=sys.stderr)
            return 1

    # Interactive mode
    try:
        shell.cmdloop()
        return 0
    except KeyboardInterrupt:
        print("\nBye")
        return 0


if __name__ == "__main__":
    sys.exit(main())
