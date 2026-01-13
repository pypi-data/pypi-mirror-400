"""
TCK Test Suites
"""

from .basic import create_basic_suite
from .documents import create_document_suite
from .folders import create_folder_suite
from .navigation import create_navigation_suite
from .properties import create_property_suite
from .repository import create_repository_suite
from .versioning import create_versioning_suite

__all__ = [
    "create_basic_suite",
    "create_repository_suite",
    "create_folder_suite",
    "create_document_suite",
    "create_property_suite",
    "create_navigation_suite",
    "create_versioning_suite",
]
