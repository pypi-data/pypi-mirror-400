.. SPDX-FileCopyrightText: 2023-2024 Anna <cyber@sysrq.in>
.. SPDX-License-Identifier: CC0-1.0

Contributing
============

Any form of contribution is welcome!

Workflow
--------

First, get the source code:

.. prompt:: bash

   git clone https://git.sysrq.in/python/repology-client

Make some changes and run the tests and the linters:

.. prompt:: bash

   tox run

Commit the changes. Your commit message should conform to the following
standard::

    file/changed: concice and complete statement of the purpose

    This is the body of the commit message.  The line above is the
    summary.  The summary should be no more than 72 chars long.  The
    body can be more freely formatted, but make it look nice.  Make
    sure to reference any bug reports and other contributors.  Make
    sure the correct authorship appears.

Use `git rebase`_ if needed to make commit history look good.

.. _git rebase: https://git-rebase.io/

Finally, send a patch to the developer using `git send-email`_:

.. prompt:: bash

   git send-email --to=cyber@sysrq.in origin/master

.. _git send-email: https://git-send-email.io/

.. note::
   If you prefer GitHub-style workflow, use the `mirror repo`_ to send pull
   requests.

.. _mirror repo: https://github.com/cybertailor/repology-client

Code style
----------

Whatever the almighty linters say. Code style should conform the `PEP 8`_
standard at least.

.. _PEP 8: https://peps.python.org/pep-0008/
