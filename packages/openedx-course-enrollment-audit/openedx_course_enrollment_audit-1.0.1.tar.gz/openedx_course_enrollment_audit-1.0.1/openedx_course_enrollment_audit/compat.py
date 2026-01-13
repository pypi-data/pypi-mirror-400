"""
Proxies and compatibility code for edx-platform features.

This module moderates access to all edx-platform features allowing for cross-version compatibility code.
It also simplifies running tests outside edx-platform's environment by stubbing these functions in unit tests.
"""

# ruff: noqa: PLC0415

from django.conf import settings


def get_manual_enrollment_audit_model():  # noqa: ANN201
    """Get the manual enrollment audit model from Open edX."""
    if getattr(settings, "TEST_OPENEDX_COURSE_ENROLLMENT_AUDIT", False):  # pragma: no cover
        # We can ignore this in the unit testing environment.
        return object

    from common.djangoapps.student.models import ManualEnrollmentAudit  # ty: ignore[unresolved-import]

    return ManualEnrollmentAudit
