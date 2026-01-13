"""
CMIS Test Compatibility Kit (TCK)

A comprehensive compliance testing suite for CMIS servers, similar to Litmus for WebDAV.
"""

from .runner import TCKRunner
from .suite import TCKTest, TCKTestSuite

__all__ = ["TCKRunner", "TCKTestSuite", "TCKTest"]
