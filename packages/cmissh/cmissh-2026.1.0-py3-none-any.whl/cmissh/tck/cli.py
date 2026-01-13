"""
CMIS TCK Command Line Interface
"""

import argparse
import sys

from .runner import TCKRunner
from .suites import (
    create_basic_suite,
    create_document_suite,
    create_folder_suite,
    create_navigation_suite,
    create_property_suite,
    create_repository_suite,
    create_versioning_suite,
)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="CMIS Test Compatibility Kit (TCK) - Test CMIS server compliance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test local Alfresco server
  cmis-tck http://localhost:8080/alfresco/api/-default-/public/cmis/versions/1.1/atom

  # Test with credentials
  cmis-tck -u admin -p admin http://localhost:8080/alfresco/api/...

  # Run specific test suites
  cmis-tck --suites basic,folders http://localhost:8080/alfresco/api/...

  # Verbose output
  cmis-tck -v http://localhost:8080/alfresco/api/...

Available test suites:
  - basic:       Basic CMIS operations (connection, CRUD)
  - repository:  Repository information and capabilities
  - folders:     Folder operations (create, navigate, delete)
  - documents:   Document operations (create, content, delete)
  - properties:  Property operations (get, update)
  - navigation:  Navigation operations (paths, descendants)
  - versioning:  Versioning operations (checkout, versions)
        """,
    )

    parser.add_argument("url", help="CMIS server URL (AtomPub binding)")

    parser.add_argument(
        "-u",
        "--username",
        default="admin",
        help="Username for authentication (default: admin)",
    )

    parser.add_argument(
        "-p",
        "--password",
        default="admin",
        help="Password for authentication (default: admin)",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose output (show capabilities and errors)",
    )

    parser.add_argument(
        "--suites",
        help="Comma-separated list of test suites to run (default: all)",
    )

    args = parser.parse_args()

    # Create runner
    runner = TCKRunner(args.url, args.username, args.password, verbose=args.verbose)

    # Determine which suites to run
    all_suites = {
        "basic": create_basic_suite,
        "repository": create_repository_suite,
        "folders": create_folder_suite,
        "documents": create_document_suite,
        "properties": create_property_suite,
        "navigation": create_navigation_suite,
        "versioning": create_versioning_suite,
    }

    if args.suites:
        suite_names = [s.strip() for s in args.suites.split(",")]
        for name in suite_names:
            if name not in all_suites:
                print(f"ERROR: Unknown test suite: {name}")
                print(f"Available suites: {', '.join(all_suites.keys())}")
                sys.exit(1)
        suites_to_run = {name: all_suites[name] for name in suite_names}
    else:
        suites_to_run = all_suites

    # Add suites to runner
    for suite_func in suites_to_run.values():
        runner.add_suite(suite_func())

    # Run all tests
    print("=" * 70)
    print("CMIS Test Compatibility Kit (TCK)")
    print("=" * 70)
    runner.run_all()


if __name__ == "__main__":
    main()
