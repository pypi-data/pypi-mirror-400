.. SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
.. SPDX-License-Identifier: CC0-1.0

Getting Started
===============

Basic example
-------------

Find out which versions projects with "firefox" in their name are packaged at:

.. code-block:: python

    import asyncio
    import repology_client

    async def main():
        projects = await repology_client.get_projects(search="firefox")
        for proj, packages in projects.items():
            for pkg in packages:
                print(f"{proj} is packaged in {pkg.repo} at version {pkg.version}")
            print("-" * 20)

    asyncio.run(main())

Get all Firefox packages as a set:

.. code-block:: python

    packages = await repology_client.get_packages(firefox)

Advanced usage
--------------

You can control timeouts and other connection settings by constructing custom
:external:py:class:`aiohttp.ClientSession` objects and passing them to a
function.

If you're making an application that makes bulk requests to Repology API, please
consider setting custom ``User-agent`` header. It usually looks like this::

    Mozilla/5.0 (compatible; <botname>/<botversion>; +<boturl>)
