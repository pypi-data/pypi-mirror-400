"""
TCK Test Runner

Executes test suites and provides litmus-style output.
"""

import re
import sys
import traceback

from cmissh.model import CmisClient

from .suite import TCKTest, TCKTestSuite, TestResult


def clean_error_message(error: Exception) -> str:
    """
    Extract a clean, user-friendly error message from an exception.
    Removes server-side tracebacks and HTML content.
    """
    error_str = str(error)

    # If it's a RuntimeException or similar with HTTP error, extract key info
    if "Error" in error_str and "at http" in error_str:
        # Extract "Error XXX at URL" and first line after it
        parts = error_str.split("\n")
        if len(parts) > 0:
            # Get the HTTP error line
            http_error = parts[0].strip()

            # Try to extract meaningful error from response
            # Remove HTML tags
            clean_parts = []
            for part in parts[1:]:
                # Skip if it contains HTML or traceback markers
                if any(
                    marker in part
                    for marker in ["<html>", "Traceback", 'File "', "  File"]
                ):
                    break
                # Try to extract error message from HTML if present
                msg_match = re.search(r"<!--message-->(.*?)<!--/message-->", part)
                if msg_match:
                    clean_parts.append(msg_match.group(1))
                    break

            if clean_parts:
                return f"{http_error.split(' Internal')[0]} - {clean_parts[0]}"
            # Just return the HTTP error line
            return http_error.split("\n")[0].split(" Internal")[0].strip()

    # For other errors, just return the first line
    error_lines = error_str.split("\n")
    return error_lines[0] if error_lines else str(error)


class TCKRunner:
    """TCK test runner with litmus-style output"""

    def __init__(self, url: str, username: str, password: str, verbose: bool = False):
        self.url = url
        self.username = username
        self.password = password
        self.verbose = verbose
        self.client: CmisClient | None = None
        self.repository = None
        self.capabilities = {}
        self.suites: list[TCKTestSuite] = []

    def add_suite(self, suite: TCKTestSuite):
        """Add a test suite to run"""
        self.suites.append(suite)

    def connect(self) -> bool:
        """Connect to CMIS server and detect capabilities"""
        try:
            print(f"-> connecting to {self.url}")
            self.client = CmisClient(self.url, self.username, self.password)
            self.repository = self.client.getDefaultRepository()

            # Detect capabilities
            caps = self.repository.getCapabilities()
            self.capabilities = {
                "ACL": caps.get("capabilityACL", "none") != "none",
                "AllVersionsSearchable": caps.get(
                    "capabilityAllVersionsSearchable", False
                ),
                "Changes": caps.get("capabilityChanges", "none") != "none",
                "ContentStreamUpdatability": caps.get(
                    "capabilityContentStreamUpdatability", "none"
                ),
                "GetDescendants": caps.get("capabilityGetDescendants", False),
                "GetFolderTree": caps.get("capabilityGetFolderTree", False),
                "Multifiling": caps.get("capabilityMultifiling", False),
                "PWCSearchable": caps.get("capabilityPWCSearchable", False),
                "PWCUpdatable": caps.get("capabilityPWCUpdatable", False),
                "Query": caps.get("capabilityQuery", "none") != "none",
                "Renditions": caps.get("capabilityRenditions", "none") != "none",
                "Unfiling": caps.get("capabilityUnfiling", False),
                "VersionSpecificFiling": caps.get(
                    "capabilityVersionSpecificFiling", False
                ),
            }

            if self.verbose:
                print("-> detected capabilities:")
                for cap, supported in self.capabilities.items():
                    status = "YES" if supported else "NO"
                    print(f"   {cap}: {status}")

            return True
        except Exception as e:
            print(f"ERROR: Failed to connect: {e}")
            return False

    def should_run_test(self, test: TCKTest) -> bool:
        """Check if test should run based on capabilities"""
        if test.required_capability:
            return self.capabilities.get(test.required_capability, False)
        return True

    def run_test(self, test: TCKTest, context: dict) -> TestResult:
        """Run a single test"""
        try:
            test.test_func(context)
            return TestResult.PASS
        except AssertionError as e:
            test.error_message = str(e)
            return TestResult.FAIL
        except Exception as e:
            # Clean up error message for display
            test.error_message = clean_error_message(e)
            if self.verbose:
                print(f"\nVerbose error details for {test.name}:")
                traceback.print_exc()
                print()
            return TestResult.FAIL

    def format_test_name(self, index: int, name: str, max_width: int = 25) -> str:
        """Format test name for display"""
        formatted = f"{index:2}. {name}"
        if len(formatted) < max_width:
            formatted += "." * (max_width - len(formatted))
        return formatted

    def print_test_result(self, index: int, test: TCKTest):
        """Print test result in litmus style"""
        name_part = self.format_test_name(index, test.name)

        if test.result == TestResult.PASS:
            if test.warnings:
                # Print warnings first
                for warning in test.warnings:
                    print(f"WARNING: {warning}")
                print(
                    f"    {name_part} pass (with {len(test.warnings)} warning{'s' if len(test.warnings) > 1 else ''})"
                )
            else:
                print(f" {name_part} pass")

        elif test.result == TestResult.FAIL:
            error_msg = test.error_message or "unknown error"
            print(f" {name_part} FAIL ({error_msg})")

        elif test.result == TestResult.SKIPPED:
            print(f" {name_part} SKIPPED")

    def run_suite(self, suite: TCKTestSuite):
        """Run a test suite"""
        print(f"-> running `{suite.name}':")

        # Create context for tests
        context = {
            "client": self.client,
            "repository": self.repository,
            "capabilities": self.capabilities,
            "runner": self,
            "suite_data": {},  # For sharing data between tests
        }

        # Run setup if defined
        if suite.setup_func:
            try:
                suite.setup_func(context)
            except Exception as e:
                error_msg = clean_error_message(e)
                print(f"ERROR: Suite setup failed: {error_msg}")
                if self.verbose:
                    print("\nVerbose error details:")
                    traceback.print_exc()
                    print()
                return

        # Run each test
        for index, test in enumerate(suite.tests):
            # Check if test should be skipped
            if not self.should_run_test(test):
                test.result = TestResult.SKIPPED
                self.print_test_result(index, test)
                continue

            # Check dependencies
            if test.depends_on:
                dep_test = next(
                    (t for t in suite.tests if t.name == test.depends_on), None
                )
                if dep_test and dep_test.result != TestResult.PASS:
                    test.result = TestResult.SKIPPED
                    self.print_test_result(index, test)
                    continue

            # Run the test
            test.result = self.run_test(test, context)
            self.print_test_result(index, test)

        # Run teardown if defined
        if suite.teardown_func:
            try:
                suite.teardown_func(context)
            except Exception as e:
                error_msg = clean_error_message(e)
                print(f"WARNING: Suite teardown failed: {error_msg}")

        # Print summary
        summary = suite.get_summary()
        total_run = summary["total"] - summary["skipped"]

        if summary["skipped"] > 0:
            print(
                f"-> {summary['skipped']} test{'s' if summary['skipped'] > 1 else ''} {'were' if summary['skipped'] > 1 else 'was'} skipped."
            )

        print(
            f"<- summary for `{suite.name}': of {total_run} tests run: "
            f"{summary['passed']} passed, {summary['failed']} failed. "
            f"{summary['percentage']:.1f}%"
        )

        if summary["warnings"] > 0:
            print(
                f"-> {summary['warnings']} warning{'s were' if summary['warnings'] > 1 else ' was'} issued."
            )

    def run_all(self):
        """Run all test suites"""
        if not self.connect():
            sys.exit(1)

        print()

        for suite in self.suites:
            self.run_suite(suite)
            print()

        # Overall summary
        total_suites = len(self.suites)
        total_tests = sum(len(s.tests) for s in self.suites)
        total_passed = sum(s.get_summary()["passed"] for s in self.suites)
        total_failed = sum(s.get_summary()["failed"] for s in self.suites)
        total_skipped = sum(s.get_summary()["skipped"] for s in self.suites)

        print("=" * 70)
        print(f"CMIS TCK Results: {total_suites} suites, {total_tests} tests")
        print(f"  Passed:  {total_passed}")
        print(f"  Failed:  {total_failed}")
        print(f"  Skipped: {total_skipped}")

        if total_failed > 0:
            sys.exit(1)
