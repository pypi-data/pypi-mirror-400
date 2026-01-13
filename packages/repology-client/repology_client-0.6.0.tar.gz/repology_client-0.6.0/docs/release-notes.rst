.. SPDX-FileCopyrightText: 2024-2026 Anna <cyber@sysrq.in>
.. SPDX-License-Identifier: CC0-1.0

Release Notes
=============

0.6.0
----------

- **Breaking**: :py:func:`repology_client.api` now takes :py:class:`yarl.URL`,
  as our cursed custom URL processing was replaced by proper :pypi:`yarl` API.

- **Gone**: Python 3.11 support.

- Stricter typing.

*Dependencies introduced:*

- :pypi:`yarl` (it was already pulled by :pypi:`aiohttp`)

0.5.0
-----

- **New**: :py:func:`repology_client.utils.format_link_status` function for
  converting status codes (returned in data objects of ``homepage_dead`` and
  ``download_dead`` problem types) to human-readable messages.

- Increase the delay between API calls.

- Fix duplicate results in problems list.

0.4.0
-----

- **Breaking**: Remove experimental API endpoints, since there are no plans to
  re-implement them in the new Repology webapp.

- **New**: :py:func:`repology_client.get_problems` function for
  ``/api/v1/repository/<repo>/problems`` and
  ``/api/v1/maintainer/<maint>/problems-for-repo/<repo>`` endpoints.

0.3.0
-----

- **Breaking**: Switch types from Pydantic dataclasses to Pydantic models.

- Use ``collections.abc`` types in return annotations (such as ``Set`` and
  ``Mapping``).

- Initiate ``TypeAdapter`` once to improve performance.

- Defer building Pydantic models until the first use.

0.2.0
-----

- **New**: :py:func:`repology_client.exp.distromap` function for
  ``/api/experimental/distromap`` endpoint.

- Parse JSON with possibly faster Pydantic parser, since we already use this
  library.

- Improve API documentation and switch to Alabaster HTML theme.

0.1.0
-----

- **New:** :py:func:`repology_client.resolve_package` function providing
  `Project by package name`__ tool's functionality.

- **Gone:** Python 3.10 support.

- Fix default session not closing properly.

__ https://repology.org/tools/project-by

0.0.2
-----

- Fix fetching >200 projects.

0.0.1
-----

- First release
