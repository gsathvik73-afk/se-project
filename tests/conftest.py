"""Attach machine-readable SRS links to JUnit evidence, including legacy suites."""
import pytest


def pytest_collection_modifyitems(items):
    for item in items:
        if not item.get_closest_marker('unit'):
            item.add_marker(pytest.mark.system)
        marker = item.get_closest_marker('requirement')
        if marker:
            item.user_properties.append(('requirement', marker.args[0]))
