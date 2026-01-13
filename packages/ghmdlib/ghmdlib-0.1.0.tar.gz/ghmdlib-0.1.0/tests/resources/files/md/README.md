# A Markdown to GitHub-style HTML file conversion utility

[![PyPI - Version](https://img.shields.io/pypi/v/ghmdlib?style=flat-square)](https://pypi.org/project/ghmdlib)
[![PyPI - Implementation](https://img.shields.io/pypi/implementation/ghmdlib?style=flat-square)](https://pypi.org/project/ghmdlib)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ghmdlib?style=flat-square)](https://pypi.org/project/ghmdlib)
[![PyPI - Status](https://img.shields.io/pypi/status/ghmdlib?style=flat-square)](https://pypi.org/project/ghmdlib)
[![Static Badge](https://img.shields.io/badge/tests-passing-brightgreen?style=flat-square)](https://pypi.org/project/ghmdlib)
[![Static Badge](https://img.shields.io/badge/code_coverage-100%25-brightgreen?style=flat-square)](https://pypi.org/project/ghmdlib)
[![Static Badge](https://img.shields.io/badge/pylint_analysis-100%25-brightgreen?style=flat-square)](https://pypi.org/project/ghmdlib)
[![Documentation Status](https://readthedocs.org/projects/ghmdlib/badge/?version=latest&style=flat-square)](https://ghmdlib.readthedocs.io/en/latest)
[![PyPI - License](https://img.shields.io/pypi/l/ghmdlib?style=flat-square)](https://opensource.org/license/mit)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/ghmdlib?style=flat-square)](https://pypi.org/project/ghmdlib)

## Overview
``ghmdlib`` (GitHub Markdown Library) is a light-weight and simple command line utility (and back-end library) designed to convert Markdown files into GitHub Flavoured HTML. It does so by using the [GitHub Markdown API][github-api] in combination with [GitHub Markdown CSS][github-css].

> [!NOTE]
> This project is a fork of the original [``ghmd``][ghmd] utility (commit [8f6a0ff][ghmd-commit]), and updated to include the following features:
>
>   - A back-end library providing callable conversion functionality to your Python applications.
>   - An 'offline' mode for sensitive environment deployment (or limited internet connectivity).
>   - Preview functionality which auto-opens converted documents in a web browser for quick viewing.

As an aside, the  ``ghmdlib`` command line utility was used for proofing this ``README.md`` file, using the following command:

```bash
$ ./ghmd.py ../README.md --preview 
```

## Quickstart

### Installation
To install `ghmdlib`, first activate your target virtual environment, then use `pip`:

```bash
pip install ghmdlib
```

This will install *both* the library and the command line utility.

For older releases, visit [PyPI][pypi-history] or the [GitHub Releases][github-releases] page.

### Command Line Utility Usage
Simply run `ghmdlib` with the path to the markdown file(s) you want to convert. An HTML file will be created in the same directory as the original markdown file with the same filename, using an ``.html`` file extension.

For example:

```bash
ghmdlib /path/to/my-file.md
```

### Library Usage
To integrate the Markdown to HTML converter into a Python project, the library can be called as:

```python
from ghmdlib import converter

# Convert a Markdown file with auto-open preview.
converter.convert(path='/path/to/my-file.md', preview=True)
```

## Command Line Utility Options

### Help Menu: ``--help``
The help menu can be accessed at any time using the following. This provides an overview of the tool's capabilities and available options.

```bash
ghmdlib --help
```

### Offline Mode: ``--offline``
If using ``ghmdlib`` in a sensitive environment, or without internet connectivity, the CLI utility and library can be used offline, making use of the pre-downloaded CSS files (for both the dark and light themes), and the ``mdtex2html`` library for Markdown to HTML conversions, rather than calling the GitHub API. 

### Themes: `--dark` and `--light`
The default CSS styles adapt to the system's dark mode setting of the reader. If you want to force the CSS to be light or dark, you can use the `--light` or `--dark` options.

For example, to render the Markdown file in dark mode, you can use:

```bash
ghmdlib /path/to/my-file.md --dark
```

Both `--light` and `--dark` can be used in combination with `--embed-css`.

### Embedded CSS: `--embed-css`
By default, ``ghmdlib`` will add the remote CSS as a ``<link>`` tag in the HTML file. If you want to embed the CSS directly into the HTML file so that, for example, you can send the HTML file to someone else and they can view it without an internet connection, you can use the `--embed-css` option.

```bash
ghmdlib /path/to/my-file.md --embed-css
```

### Plain Markdown: `--no-gfm`
The tool offers two modes: GitHub Flavored Markdown (``gfm`` by default) and plain Markdown. To use the latter, the `--no-gfm` option can be used:

```bash
ghmdlib /path/to/my-file.md --no-gfm
```

### GitHub API Token
By default, ``ghmdlib`` uses unauthenticated requests to the GitHub API, which has a rate limit of 60 requests per hour. To increase this limit to 5000 requests per hour, you can set the ``GITHUB_TOKEN`` environment variable with a GitHub personal access token:

```bash
export GITHUB_TOKEN=your_github_token_here
```

To create a personal access token, visit your [GitHub Settings > Developer Settings > Personal access tokens](https://github.com/settings/tokens) and create a new token (no specific scopes are required).

## Using the Library
The documentation suite provides detailed explanations and usage examples for each importable module. For in-depth documentation, code examples, and source links, refer to the [Library API][api] page.

A **search** field is available in the left navigation bar to help you quickly locate specific modules or methods.

## Troubleshooting
No troubleshooting guidance is available at this time.

For questions not covered here, or to report bugs, issues, or suggestions, please open an issue on [GitHub][github].

[api]: https://ghmdlib.readthedocs.io/en/latest/
[model]: https://docling-project.github.io/docling/usage/advanced_options/#model-prefetching-and-offline-usage
[ghmd]: https://github.com/roman910dev/ghmd
[ghmd-commit]: https://github.com/roman910dev/ghmd/commit/8f6a0ffd798f8954f7d04d08b668235d623001fc
[github]: https://github.com/s3dev/ghmdlib
[github-api]: https://docs.github.com/en/rest/markdown/markdown
[github-css]: https://github.com/sindresorhus/github-markdown-css
[github-releases]: https://github.com/s3dev/ghmdlib/releases
[gpu-support]: https://docling-project.github.io/docling/usage/gpu/
[pypi-history]: https://pypi.org/project/ghmdlib/#history

