openedx-course-enrollment-audit
###############################

|pypi-badge| |ci-badge| |codecov-badge| |doc-badge| |pyversions-badge|
|license-badge| |status-badge|

Purpose
*******

This plugin optimizes the tracking and auditing of manual enrollments in Open edX courses by:

1. Parsing and storing JSON data from the ``reason`` field of the ``ManualEnrollment`` model.
2. Ensuring that each ``enrolled_email`` and ``course_id`` pair is unique.

Getting Started
***************

Developing
==========

One-Time Setup
--------------
.. code-block:: bash

  # Clone the repository
  git clone git@github.com:open-craft/openedx-course-enrollment-audit.git
  cd openedx-course-enrollment-audit

  # Set up a virtualenv using virtualenvwrapper with the same name as the repo and activate it
  mkvirtualenv -p python3.11 openedx-course-enrollment-audit

Tutor Installation
------------------

To install this plugin using Tutor:

.. code-block:: bash

  # Mount the directory in Tutor
  tutor mounts add openedx:/local/projects/shared-src:/openedx/shared-src

  # Install the package
  tutor dev exec lms pip install -e /openedx/shared-src/openedx-course-enrollment-audit

  # Run migrations
  tutor dev exec lms ./manage.py lms migrate openedx_course_enrollment_audit

Every time you develop something in this repo
---------------------------------------------
.. code-block::

  # Activate the virtualenv
  workon openedx-course-enrollment-audit

  # Grab the latest code
  git checkout main
  git pull

  # Install/update the dev requirements
  make requirements

  # Run the tests and quality checks (to verify the status before you make any changes)
  make validate

  # Make a new branch for your changes
  git checkout -b <your_github_username>/<short_description>

  # Using your favorite editor, edit the code to make your change.
  vim ...

  # Run static analysis and packaging tests
  make test

  # Run integration tests within Tutor
  tutor dev exec lms -- bash -c "cd /openedx/shared-src/openedx-course-enrollment-audit && make test_integration"

  # Commit all your changes
  git commit ...
  git push

  # Open a PR and ask for review.

Deploying
=========

Native Installation
-------------------

To deploy this to an Open edX instance, include it in the ``EDXAPP_PRIVATE_REQUIREMENTS`` or ``EDXAPP_EXTRA_REQUIREMENTS`` variables.

Tutor Installation
------------------

To `install`_ this in the Open edX build, include it in the ``config.yml`` file using the ``OPENEDX_EXTRA_PIP_REQUIREMENTS`` variable.

You need to rebuild the Open edX image:

.. code-block:: bash

  tutor images build openedx


.. _install: https://docs.tutor.overhang.io/configuration.html?highlight=xblock#installing-extra-xblocks-and-requirements


Documentation
*************

Usage
=====

You can inspect the records by importing the ``CourseEnrollmentAudit`` model in your Django shell:

.. code-block:: python

  from openedx_course_enrollment_audit.models import CourseEnrollmentAudit
  CourseEnrollmentAudit.objects.all()

Alternatively, you can access them directly from the database shell:

.. code-block:: sql

  ./manage.py lms dbshell
  SELECT * FROM openedx_course_enrollment_audit_courseenrollmentaudit;

Backfilling Existing Data
=========================

To backfill existing data from ``ManualEnrollmentAudit`` into ``CourseEnrollmentAudit``, run the following management command:

.. code-block:: bash

  ./manage.py lms backfill_course_enrollment_audit

This command ensures that all existing manual enrollments are tracked and audited according to the plugin's logic.

Getting Help
============

If you're having trouble, we have discussion forums at
https://discuss.openedx.org where you can connect with others in the
community.

Our real-time conversations are on Slack. You can request a `Slack
invitation`_, then join our `community Slack workspace`_.

For anything non-trivial, the best path is to open an issue in this
repository with as many details about the issue you are facing as you
can provide.

https://github.com/open-craft/openedx-course-enrollment-audit/issues

For more information about these options, see the `Getting Help`_ page.

.. _Slack invitation: https://openedx.org/slack
.. _community Slack workspace: https://openedx.slack.com/
.. _Getting Help: https://openedx.org/getting-help

License
*******

The code in this repository is licensed under the AGPL 3.0 unless
otherwise noted.

Please see `LICENSE.txt <LICENSE.txt>`_ for details.

Contributing
************

Contributions are very welcome.
Please read `How To Contribute <https://openedx.org/r/how-to-contribute>`_ for details.

This project is currently accepting all types of contributions, bug fixes,
security fixes, maintenance work, or new features.  However, please make sure
to have a discussion about your new feature idea with the maintainers prior to
beginning development to maximize the chances of your change being accepted.
You can start a conversation by creating a new issue on this repo summarizing
your idea.

The Open edX Code of Conduct
****************************

All community members are expected to follow the `Open edX Code of Conduct`_.

.. _Open edX Code of Conduct: https://openedx.org/code-of-conduct/

People
******

The assigned maintainers for this component and other project details may be
found in `Backstage`_. Backstage pulls this data from the ``catalog-info.yaml``
file in this repo.

.. _Backstage: https://open-edx-backstage.herokuapp.com/catalog/default/component/openedx-course-enrollment-audit

Reporting Security Issues
*************************

Please do not report security issues in public. Please email security@tcril.org.

.. |pypi-badge| image:: https://img.shields.io/pypi/v/openedx-course-enrollment-audit.svg
    :target: https://pypi.python.org/pypi/openedx-course-enrollment-audit/
    :alt: PyPI

.. |ci-badge| image:: https://github.com/open-craft/openedx-course-enrollment-audit/workflows/Python%20CI/badge.svg?branch=main
    :target: https://github.com/open-craft/openedx-course-enrollment-audit/actions
    :alt: CI

.. |codecov-badge| image:: https://codecov.io/github/open-craft/openedx-course-enrollment-audit/coverage.svg?branch=main
    :target: https://codecov.io/github/open-craft/openedx-course-enrollment-audit?branch=main
    :alt: Codecov

.. |doc-badge| image:: https://readthedocs.org/projects/openedx-course-enrollment-audit/badge/?version=latest
    :target: https://openedx-course-enrollment-audit.readthedocs.io/en/latest/
    :alt: Documentation

.. |pyversions-badge| image:: https://img.shields.io/pypi/pyversions/openedx-course-enrollment-audit.svg
    :target: https://pypi.python.org/pypi/openedx-course-enrollment-audit/
    :alt: Supported Python versions

.. |license-badge| image:: https://img.shields.io/github/license/open-craft/openedx-course-enrollment-audit.svg
    :target: https://github.com/open-craft/openedx-course-enrollment-audit/blob/main/LICENSE.txt
    :alt: License

.. |status-badge| image:: https://img.shields.io/badge/Status-Maintained-brightgreen
