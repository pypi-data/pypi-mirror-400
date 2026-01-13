"""openedx_course_enrollment_audit Django application initialization."""

from typing import ClassVar

from django.apps import AppConfig


class OpenedxCourseEnrollmentAuditConfig(AppConfig):
    """Configuration for the openedx_course_enrollment_audit Django application."""

    name = "openedx_course_enrollment_audit"

    plugin_app: ClassVar[dict] = {
        "signals_config": {
            "lms.djangoapp": {
                "relative_path": "signals",
            },
        },
    }

    def ready(self):
        """Import signals so they are registered."""
        from openedx_course_enrollment_audit import signals  # noqa: F401, PLC0415
