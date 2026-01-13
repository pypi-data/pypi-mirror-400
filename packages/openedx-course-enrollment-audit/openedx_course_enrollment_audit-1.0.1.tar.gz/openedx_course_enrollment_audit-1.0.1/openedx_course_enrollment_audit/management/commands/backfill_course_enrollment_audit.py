"""
Management command to backfill CourseEnrollmentAudit records from existing ManualEnrollmentAudit records.

This command is intended to initialize the CourseEnrollmentAudit table by creating or updating records
for all existing ManualEnrollmentAudit entries. It should be run when deploying changes that introduce
the CourseEnrollmentAudit model to ensure historical data is captured.

Usage:
    ./manage.py lms backfill_course_enrollment_audit

Note:
    - The command iterates over all ManualEnrollmentAudit records and processes them one by one.
    - Progress messages are displayed every `batch_size` records.
    - The command can be safely re-run; existing CourseEnrollmentAudit records will be updated.
"""

from django.core.management.base import BaseCommand

from openedx_course_enrollment_audit.compat import get_manual_enrollment_audit_model
from openedx_course_enrollment_audit.models import CourseEnrollmentAudit

ManualEnrollmentAudit = get_manual_enrollment_audit_model()


class Command(BaseCommand):  # noqa: D101
    help = "Backfill CourseEnrollmentAudit from ManualEnrollmentAudit"

    def handle(self, *_args, **_kwargs):  # noqa: D102
        total_count = ManualEnrollmentAudit.objects.count()
        self.stdout.write(self.style.NOTICE(f"Starting backfill of {total_count} records from ManualEnrollmentAudit."))

        batch_size = 10000
        for i, manual_enrollment in enumerate(ManualEnrollmentAudit.objects.all().iterator(), 1):
            CourseEnrollmentAudit.create_from_manual_enrollment(manual_enrollment)

            if i % batch_size == 0:  # pragma: no cover
                self.stdout.write(self.style.SUCCESS(f"Processed {i} records..."))

        self.stdout.write(self.style.SUCCESS("Backfill completed successfully."))
