.. SPDX-FileCopyrightText: 2023 Anna <cyber@sysrq.in>
.. SPDX-License-Identifier: CC0-1.0

Installation
============

.. note::

   This library follows the `Semantic Versioning 2.0.0
   <https://semver.org/spec/v2.0.0.html>`_ policy.

Prerequisites
-------------

The following dependencies are used by this library:

* :external+aiohttp:doc:`aiohttp <index>`
* `pydantic`_ (with direct use of pydantic-core)

.. _pydantic: https://pydantic.dev/

Gentoo
------

This library is packaged for Gentoo in the GURU ebuild repository.

.. prompt:: bash #

   eselect repository enable guru
   emaint sync -r guru
   emerge dev-python/repology-client

Manual installation
-------------------

.. prompt:: bash

   pip install repology-client --user
