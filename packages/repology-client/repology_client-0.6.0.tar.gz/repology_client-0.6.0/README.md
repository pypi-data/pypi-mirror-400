<!-- SPDX-FileCopyrightText: 2023-2024 Anna <cyber@sysrq.in> -->
<!-- SPDX-License-Identifier: CC0-1.0 -->

repology-client
===============

[![Build Status](https://drone.tildegit.org/api/badges/CyberTaIlor/repology-client/status.svg)](https://drone.tildegit.org/CyberTaIlor/repology-client)
[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/8828/badge)](https://www.bestpractices.dev/projects/8828)

Asynchronous wrapper for [Repology API][repology-api].

> Note that API stability is currently not guaranteed - it may change at any
> moment.

[repology-api]: https://repology.org/api


Installing
----------

### Gentoo

```sh
eselect repository enable guru
emaint sync -r guru
emerge dev-python/repology-client
```

### Other systems

`pip install repology-client --user`


Packaging
---------

You can track new releases using an [RSS feed][rss] provided by PyPI.

[rss]: https://pypi.org/rss/project/repology-client/releases.xml


Contributing
------------

Patches and pull requests are welcome. Please use either [git-send-email(1)][1]
or [git-request-pull(1)][2], addressed to <cyber@sysrq.in>.

If you prefer GitHub-style workflow, use the [mirror repo][gh] to send pull
requests.

Your commit message should conform to the following standard:

```
file/changed: Concice and complete statement of the purpose

This is the body of the commit message.  The line above is the
summary.  The summary should be no more than 72 chars long.  The
body can be more freely formatted, but make it look nice.  Make
sure to reference any bug reports and other contributors.  Make
sure the correct authorship appears.
```

[1]: https://git-send-email.io/
[2]: https://git-scm.com/docs/git-request-pull
[gh]: http://github.com/cybertailor/repology-client


IRC
---

You can join the `#repology-client` channel either on [OFTC][oftc] or
[via Matrix][matrix].

[oftc]: https://www.oftc.net/
[matrix]: https://matrix.to/#/#repology-client:sysrq.in


License
-------

European Union Public License 1.2
