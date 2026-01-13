"""Signals for openedx_course_enrollment_audit app."""

from django.db.models.signals import post_save
from django.dispatch import receiver

from openedx_course_enrollment_audit.compat import get_manual_enrollment_audit_model
from openedx_course_enrollment_audit.models import CourseEnrollmentAudit

ManualEnrollmentAudit = get_manual_enrollment_audit_model()


@receiver(post_save, sender=ManualEnrollmentAudit)
def sync_course_enrollment_audit(sender, instance, created, **_kwargs):  # noqa: ARG001, ANN001
    """Signal to sync CourseEnrollmentAudit with ManualEnrollmentAudit."""
    CourseEnrollmentAudit.create_from_manual_enrollment(instance)
