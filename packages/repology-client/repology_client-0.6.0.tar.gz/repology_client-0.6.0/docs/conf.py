# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2023-2026 Anna <cyber@sysrq.in>

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'repology-client'
author = 'Anna Vyalkova'
copyright = f'2024, {author}'
release = '0.6.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autosummary',
    'sphinx.ext.autodoc',
    'sphinx.ext.extlinks',
    'sphinx.ext.intersphinx',
    'sphinx_prompt',
]

try:
    import notfound.extension
    extensions.append('notfound.extension')

    notfound_urls_prefix = None
except ModuleNotFoundError:
    pass

try:
    import sphinx_sitemap
    extensions.append('sphinx_sitemap')

    sitemap_locales = [None]
    sitemap_url_scheme = '{link}'
    sitemap_excludes = [
        '404.html',
    ]
    sitemap_show_lastmod = True
except ModuleNotFoundError:
    pass

try:
    import sphinxcontrib.spelling
    extensions.append('sphinxcontrib.spelling')

    spelling_word_list_filename='spelling_wordlist.txt'
except ModuleNotFoundError:
    pass

master_doc = 'index'
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

extlinks = {
    'bug': ('https://bugs.sysrq.in/show_bug.cgi?id=%s', 'bug #%s'),
    'gitweb': (f'https://git.sysrq.in/python/{project}/tree/%s', '%s'),
    'pypi': ('https://pypi.org/project/%s/', '%s'),
}
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'aiohttp': ('https://docs.aiohttp.org/en/stable', None),
    'pydantic': ('https://docs.pydantic.dev/latest/', None),
    'yarl': ('https://yarl.aio-libs.org/en/stable', None),
}

autosummary_generate = False
autodoc_default_options = {
    'show-inheritance': True,
    'undoc-members': True,
    'member-order': 'bysource',
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_permalinks_icon = '#'
html_theme_options = {
    'description': 'Asynchronous Python wrapper for Repology API',
    'canonical_url': 'https://repology-client.sysrq.in/',
}
html_sidebars = {
    '**': [
        'about.html',
        'navigation.html',
        'searchbox.html',
    ]
}

html_static_path = ['_static']
html_title = f'{project} {release}'
html_baseurl = 'https://repology-client.sysrq.in/'
