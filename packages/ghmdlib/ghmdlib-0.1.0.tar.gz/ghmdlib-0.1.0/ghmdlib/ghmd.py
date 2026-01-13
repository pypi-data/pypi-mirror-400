#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:App:       ghmd(lib)
:Purpose:   This library and command line tool are designed to convert
            Markdown files into GitHub-style HTML format.

            This module provides *both* the project's command line
            interface and back-end library.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  This project is a fork of the `ghmd`_ project and has been
            updated to include an installable library to interface with
            your other Python applications. Additionally, the command
            line interface has been updated to include additional
            features.


.. _ghmd: https://github.com/roman910dev/ghmd

"""
# pylint: disable=wrong-import-order

import logging
import os
import re
import sys
import webbrowser
# locals
try:  # nocover
    from libs.argparser import argparser
    from libs._download import Download
    from libs._offline import Offline
    from libs._online import Online
except ImportError:
    from ghmdlib.libs.argparser import argparser
    from ghmdlib.libs._download import Download
    from ghmdlib.libs._offline import Offline
    from ghmdlib.libs._online import Online

logger = logging.getLogger(__name__)


class Converter:
    """Primary Markdown to HTML document conversion class.

    :Example:

        Convert a Markdown file to GitHub-style HTML::

            >>> from ghmdlib import converter

            >>> converter.convert(path='/path/to/file.md', preview=True)


        Convert a Markdown file to GitHub-style HTML, in **offline**
        mode::

            >>> from ghmdlib import converter

            >>> converter.convert(path='/path/to/file.md', offline=True)

    """

    _TEMPLATE = './resources/md-template.html'
    _RE_TITLE = re.compile(r'^# (.*)$')

    def __init__(self) -> None:
        """GitHub-Markdown converter class initialiser."""
        self._argp = None
        self._args = None
        self._css = ''
        self._headers = ''
        self._offline = False

    def convert(self,
                path: str | list[str],
                *,
                theme: str='dark',
                embed_css: bool=False,
                no_gfm: bool=False,
                offline: bool=False,
                preview: bool=False) -> bool:
        """Convert the given path(s) from Markdown to GitHub-style HTML.

        .. note::

            Once converted, the HTML file is created in the same
            directory as the source file, with the same filename and an
            '.html' file extension.

        Args:
            path (str | list[str]): Full path to the Markdown file
                (or list of files) to be converted.
            theme (str, optional): Theme to be used for the HTML.
                Options: 'dark', 'light'. Defaults to 'dark'.
            embed_css (bool, optional): Embed the CSS in the HTML file
                rather than linking. Defaults to False.
            no_gfm (bool, optional): Disable GitHub Flavoured Markdown
                (GFM) and use the standard format. Defaults to False.
            offline (bool, optional): Keep offline. Use cached CSS and
                local conversion libraries rather than the GitHub API.
            preview (bool, optional): Open each converted HTML file in
                a web browser to view the results. Defaults to False.

        Returns:
            bool: True if the conversion is successful, otherwise False.

        """
        # pylint: disable=multiple-statements
        self._offline = offline
        if isinstance(path, str):
            path = [path]
        s = self._set_css(theme=theme, embed_css=embed_css)
        if s: s = self._set_headers()
        if s: s = self._convert(path=path, mode='markdown' if no_gfm else 'gfm', preview=preview)
        return s

    def _convert(self, path: str | list[str], mode: str, preview: bool) -> bool:
        """Convert Markdown file(s) to HTML.

        Args:
            path (str | list[str]): Full path to the Markdown file
                (or list of files) to be converted.
            mode (str): Mode for Markdown conversion ('markdown' | 'gfm').
            preview (bool): Open each converted HTML file in a web
                browser to view the results.

        Returns:
            bool: True if all files were created, otherwise False.

        """
        created = []
        for file in path:
            logger.debug('Converting: %s', file)
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()
                s = self._RE_TITLE.search(content, re.MULTILINE)
                title = s.group(1) if s else ''
                tmp = self._read_template()
                if self._offline:
                    html = Offline.convert(content=content)
                else:
                    html = Online.convert(content=content, headers=self._headers, mode=mode)
                fn = f'{os.path.splitext(file)[0]}.html'
                with open(fn, 'w+', encoding='utf-8') as f:
                    f.write(tmp.replace("{{ .CSS }}", self._css)
                            .replace("{{ .Title }}", title)
                            .replace("{{ .Content }}", html))
                    created.append(fn)
            logger.debug('Created: %s', fn)
        if preview:  # nocover
            self._preview(paths=created)
        return all(map(os.path.exists, created)) or not created

    def _main(self) -> None:  # nocover  # Core functionality is covered by unittests.
        """Main CLI program entry-point and process controller.

        Exits with exit code 0 if all files were created, or the CSS
        files were downloaded successfully. Otherwise, the exit code is
        set to 2.

        .. caution::

            This method is the **command line entry-point** *only* and
            should *not* be used internally.

        """
        self._parse_args()
        if self._args.download:
            s = Download.download()
        else:
            s = self.convert(path=self._args.PATH,
                             theme='dark' if self._args.dark else 'light',
                             embed_css=self._args.embed_css,
                             no_gfm=self._args.no_gfm,
                             offline=self._args.offline,
                             preview=self._args.preview)
        sys.exit(0 if s else 2)

    def _parse_args(self) -> None:  # nocover
        """Parse CLI arguments into class attributes."""
        self._argp = argparser
        self._argp.parse()
        self._args = self._argp.args

    def _preview(self, paths: list[str]) -> None:  # nocover
        """Preview all created HTML files in a web browser.

        Args:
            paths (list[str]): A list of file paths to be previewed.

        """
        for path in paths:
            logger.debug('Opening preview for: %s', os.path.basename(path))
            webbrowser.open(path)

    def _read_template(self) -> str:
        """Read the Markdown HTML template file.

        Returns:
            str: A string containing the Markdown template.

        """
        tmp = ''
        _dir = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(_dir, self._TEMPLATE), 'r', encoding='utf-8') as f:
            tmp = f.read()
        return tmp

    def _set_css(self, theme: str, embed_css: bool) -> bool:
        """Get and set the CSS for the HTML output.

        Args:
            theme (str): Theme to be used (dark | light).
            embed_css (bool): Embed the CSS rather than linking.

        Raises:
            ValueError: If the CSS could not be retrieved.

        Returns:
            bool: True if the CSS was set successfully, otherwise False.

        """
        if self._offline:
            css = Offline.set_css(theme=theme)
        else:
            css = Online.set_css(theme=theme, embed_css=embed_css)
        self._css = css
        logger.debug('CSS retrieved successfully: %s', bool(css))
        logger.debug('CSS (truncated): %s ... %s', css[:25], css[-25:])
        return bool(css)

    def _set_headers(self) -> bool:
        """Set the HTTP headers.

        Returns:
            bool: True if the header is set, otherwise False.

        """
        self._headers = {"Accept": "application/vnd.github+json"}
        if github_token := os.environ.get("GITHUB_TOKEN"):
            self._headers["Authorization"] = f"Bearer {github_token}"
        logger.debug('Headers set successfully: %s', bool(self._headers))
        logger.debug('Header: %s', self._headers)
        return bool(self._headers)


# Alias for_library imports.
converter = Converter()

# %% Prevent from running on module import.

# pylint: disable=protected-access  # Converter._main
# Enable running as either a script (dev/debugging) or as an executable.
if __name__ == '__main__':  # pragma: nocover
    c = Converter()
    c._main()
else:  # pragma: nocover
    def main():
        """Entry-point exposed for the executable.

        The ``"ghmdlib.ghmd:main"`` value is set in ``pyproject.toml``'s
        ``[project.scripts]`` table as the entry-point for the installed
        executable.

        """
        # pylint: disable=redefined-outer-name
        c = Converter()
        c._main()
