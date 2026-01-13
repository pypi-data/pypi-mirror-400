"""
TCK Test Suite Framework
"""

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum


class TestResult(Enum):
    """Test result status"""

    PASS = "pass"
    FAIL = "fail"
    SKIPPED = "skipped"
    WARNING = "warning"


@dataclass
class TCKTest:
    """A single TCK test"""

    name: str
    description: str
    test_func: Callable
    required_capability: str | None = None
    depends_on: str | None = None

    def __post_init__(self):
        self.result: TestResult | None = None
        self.warnings: list[str] = []
        self.error_message: str | None = None


class TCKTestSuite:
    """A suite of related TCK tests"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.tests: list[TCKTest] = []
        self.setup_func: Callable | None = None
        self.teardown_func: Callable | None = None

    def add_test(
        self,
        name: str,
        description: str,
        test_func: Callable,
        required_capability: str | None = None,
        depends_on: str | None = None,
    ):
        """Add a test to the suite"""
        test = TCKTest(name, description, test_func, required_capability, depends_on)
        self.tests.append(test)
        return test

    def set_setup(self, func: Callable):
        """Set suite setup function"""
        self.setup_func = func

    def set_teardown(self, func: Callable):
        """Set suite teardown function"""
        self.teardown_func = func

    def get_summary(self) -> dict:
        """Get test results summary"""
        total = len(self.tests)
        passed = sum(1 for t in self.tests if t.result == TestResult.PASS)
        failed = sum(1 for t in self.tests if t.result == TestResult.FAIL)
        skipped = sum(1 for t in self.tests if t.result == TestResult.SKIPPED)
        warnings = sum(len(t.warnings) for t in self.tests)

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "warnings": warnings,
            "percentage": (passed / (total - skipped) * 100)
            if (total - skipped) > 0
            else 0,
        }
