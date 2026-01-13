
.. _library-api:

=========================
Library API Documentation
=========================
The page contains simple library usage examples and the module-level
documentation for each of the importable modules in ``ghmdlib``.

.. contents::
    :local:
    :depth: 1

Use Cases
=========
To save digging through the documentation for each module and cobbling
together what a 'standard use case' may look like, a couple have been
provided here.

Convert a Markdown file into GitHub-style HTML:

.. code-block:: python

    >>> from ghmdlib import converter

    >>> converter.convert(path='/path/to/my-file.md')

Convert a Markdown file into GitHub-style HTML, with auto-open preview:

.. code-block:: python

    >>> from ghmdlib import converter

    >>> converter.convert(path='/path/to/my-file.md', preview=True)

Convert a Markdown file into GitHub-style HTML, with auto-open preview
and a 'light' colour theme:

.. code-block:: python

    >>> from ghmdlib import converter

    >>> converter.convert(path='/path/to/my-file.md', preview=True, theme='light')

Convert a Markdown file into standard Markdown (not GitHub-style), with 
embedded CSS:

.. code-block:: python

    >>> from ghmdlib import converter

    >>> converter.convert(path='/path/to/my-file.md', no_gfm=True, embed_css=True)

Offline Use
-----------
In the event ``ghmdlib`` is being deployed to a secure (or otherwise 
sensitive) environment, or with limited internet access, the library can be
used **offline**.

Specifically, offline mode uses the internal CSS files for theme styling
and the ``mdtex2html`` library for conversion, rather than the GitHub API.

.. code-block:: python

    >>> from ghmdlib import converter

    >>> converter.convert(path='/path/to/my-file.md', offline=True)





Module Documentation
====================
In addition to the module-level documentation, most of the public
classes and/or methods come with one or more usage examples and access
to the source code itself.

There are two type of modules listed here:

    - Those whose API is designed to be accessed by the user/caller
    - Those which are designated 'private' and designed only for internal
      use

We've exposed both here for completeness and to aid in understanding how
the library is implemented:

.. toctree::
   :maxdepth: 1

   ghmd

|lastupdated|
