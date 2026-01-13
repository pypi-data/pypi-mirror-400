.. SPDX-FileCopyrightText: 2023-2024 Anna <cyber@sysrq.in>
.. SPDX-License-Identifier: CC0-1.0

Welcome to repology-client
==========================

Asynchronous Python wrapper for `Repology API`_.

.. _Repology API: https://repology.org/api

.. note::
    Repology API stability is currently not guaranteed – it may change at any
    moment.

If you want to learn how and why to use this library, check out the following
resources:

* :doc:`faq`
* :doc:`installation`
* :doc:`getting-started`

If you need help, or want to talk to the developers, use our chat rooms:

* IRC: `#repology-client`_ at ``irc.oftc.net``
* Matrix: `#repology-client:sysrq.in`_

.. _#repology-client: https://webchat.oftc.net/?randomnick=1&channels=repology-client&prompt=1
.. _#repology-client\:sysrq.in: https://matrix.to/#/#repology-client:sysrq.in

If you find any bugs, please report them on `Bugzilla`_.

.. _Bugzilla: https://bugs.sysrq.in/enter_bug.cgi?product=Python%20libraries&component=repology-client

Features
--------

The following endpoints are supported:

* ``/api/v1/maintainer/<maint>/problems-for-repo/<repo>``
* ``/api/v1/project/<project>``
* ``/api/v1/projects/``
* ``/api/v1/repository/<repo>/problems``
* ``/tools/project-by``

Need more? Your :doc:`contributions <contributing>` are welcome!

Table of Contents
-----------------

.. toctree::
   :caption: Documentation

   installation
   getting-started
   faq
   contributing
   release-notes
   reference

.. toctree::
   :caption: External Links

   Git Repository <https://git.sysrq.in/python/repology-client>
   PyPI Package <https://pypi.org/project/repology-client/>

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
