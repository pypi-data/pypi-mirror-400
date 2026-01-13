=============================
ghmdlib Library Documentation
=============================

.. contents:: Page Contents
    :local:
    :depth: 1

Overview
========
``ghmdlib`` (GitHub Markdown Library) is a light-weight and simple command
line utility (and back-end library) designed to convert Markdown files 
into GitHub Flavoured HTML. It does so by using the 
`GitHub Markdown API <github-api_>`_ in combination with 
`GitHub Markdown CSS <github-css_>`_.

.. note::
    This project is a fork of the original `ghmd`_ utility 
    (commit `8f6a0ff <ghmd-commit_>`_), and updated to include the 
    following features:

        - A back-end library providing callable conversion functionality 
          to your Python applications.
        - An 'offline' mode for sensitive environment deployment (or 
          limited internet connectivity).
        - Preview functionality which auto-opens converted documents in a 
          web browser for quick viewing.

Quickstart
==========

Installation
------------
To install ``ghmdlib``, first activate your target virtual environment,
then use ``pip``::

    pip install ghmdlib

For older releases, visit `PyPI <pypi-history_>`_ or the
`GitHub Releases <github-releases_>`_ page.

Command Line Utility Usage
--------------------------
Simply run ``ghmdlib`` with the path to the markdown file(s) you want to 
convert. An HTML file will be created in the same directory as the 
original markdown file with the same filename, using an ``.html`` file 
extension.

For example:

.. code-block:: bash

    ghmdlib /path/to/my-file.md

Library Usage
-------------
To integrate the Markdown to HTML converter into a Python project, the 
library can be called as:

.. code-block:: python

    from ghmdlib import converter

    # Convert a Markdown file with auto-open preview.
    converter.convert(path='/path/to/my-file.md', preview=True)

Command Line Utility Options
============================

Help Menu: ``--help``
---------------------
The help menu can be accessed at any time using the following. This 
provides an overview of the tool's capabilities and available options.

.. code-block:: bash
    
    ghmdlib --help

Offline Mode: ``--offline``
---------------------------
If using ``ghmdlib`` in a sensitive environment, or without internet 
connectivity, the CLI utility and library can be used offline, making use
of the pre-downloaded CSS files (for both the dark and light themes), 
and the ``mdtex2html`` library for Markdown to HTML conversions, rather 
than calling the GitHub API. 

Themes: ``--dark`` and ``--light``
----------------------------------
The default CSS styles adapt to the system's dark mode setting of the 
reader. If you want to force the CSS to be light or dark, you can use 
the ``--light`` or ``--dark`` options.

For example, to render the Markdown file in dark mode, you can use:

.. code-block:: bash

    ghmdlib /path/to/my-file.md --dark

Both ``--light`` and ``--dark`` can be used in combination with 
``--embed-css``.

Embedded CSS: ``--embed-css``
-----------------------------
By default, ``ghmdlib`` will add the remote CSS as a ``<link>`` tag in the
HTML file. If you want to embed the CSS directly into the HTML file so 
that, for example, you can send the HTML file to someone else and they can
view it without an internet connection, you can use the ``--embed-css``
option.

.. code-block:: bash
    
    ghmdlib /path/to/my-file.md --embed-css

Plain Markdown: ``--no-gfm``
----------------------------
The tool offers two modes: GitHub Flavored Markdown (``gfm`` by default) 
and plain Markdown. To use the latter, the ``--no-gfm`` option can be used:

.. code-block:: bash

    ghmdlib /path/to/my-file.md --no-gfm

GitHub API Token
----------------
By default, ``ghmdlib`` uses unauthenticated requests to the GitHub API,
which has a `rate limit <github-ratelimit_>`_ of 60 requests per hour. To 
increase this limit to 5000 requests per hour, you can set the ``GITHUB_TOKEN``
environment variable with a GitHub personal access token:

.. code-block:: bash

    export GITHUB_TOKEN=your_github_token_here

To create a `personal access token <github-tokens_>`_, visit your 
``GitHub Settings > Developer Settings > Personal access tokens`` 
and create a new token (no specific scopes are required).

Using the Library
=================
This documentation provides detailed explanations and usage examples for
each importable module. For in-depth documentation, code examples, and
source links, refer to the :ref:`library-api` page.

A **search** field is available in the left navigation bar to help you
quickly locate specific modules or methods.

Troubleshooting
===============
No troubleshooting guidance is available at this time.

For questions not covered here, or to report bugs, issues, or suggestions,
please :ref:`contact us <contact-us>` or open an issue on `GitHub <github_>`_.

Documentation Contents
======================
.. toctree::
    :maxdepth: 1

    library
    changelog
    contact

Indices and Tables
==================
* :ref:`genindex`
* :ref:`modindex`

.. _api: https://ghmdlib.readthedocs.io/en/latest/
.. _model: https://docling-project.github.io/docling/usage/advanced_options/#model-prefetching-and-offline-usage
.. _ghmd: https://github.com/roman910dev/ghmd
.. _ghmd-commit: https://github.com/roman910dev/ghmd/commit/8f6a0ffd798f8954f7d04d08b668235d623001fc
.. _github: https://github.com/s3dev/ghmdlib
.. _github-api: https://docs.github.com/en/rest/markdown/markdown
.. _github-css: https://github.com/sindresorhus/github-markdown-css
.. _github-ratelimit: https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api
.. _github-releases: https://github.com/s3dev/ghmdlib/releases
.. _github-tokens: https://github.com/settings/tokens
.. _gpu-support: https://docling-project.github.io/docling/usage/gpu/
.. _pypi-history: https://pypi.org/project/ghmdlib/#history


|lastupdated|

