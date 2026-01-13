#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides the functionality for **offline**
            conversions.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  This module is designed for internal use only.

"""
# pylint: disable=wrong-import-order

import logging
import mdtex2html
import os
from glob import glob

# Silence debugging output from the markdown converter.
logging.getLogger('MARKDOWN').setLevel(logging.ERROR)


class Offline:
    """This class provides the functions used for offline conversions.

    Specifically, this class uses locally cached CSS files and local
    libraries for Markdown to HTML conversions, rather than using the
    GitHub API.

    """

    _DIR_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    _DIR_RESC = os.path.join(_DIR_ROOT, 'resources')
    _EXTS = ["admonition",
             "codehilite",
             "fenced_code",
             "footnotes",
             "smarty",
             "tables",
             "toc"]

    @classmethod
    def convert(cls, content: str) -> str:
        """Convert Markdown file(s) to HTML.

        Args:
            content (str): Markdown file content to be converted.

        Returns:
            str: A string containing the Markdown content converted to
            HTML.

        """
        return mdtex2html.convert(content, extensions=cls._EXTS)

    @classmethod
    def set_css(cls, theme: str) -> str:
        """Get and set the CSS for the HTML output.

        Args:
            theme (str): Theme to be used (dark | light).

        Returns:
            str: A string containing either the CSS for the desired
            theme.

        """
        css = ''
        files = glob(os.path.join(cls._DIR_RESC, f'*-{theme}.min.css'))
        if not files:
            msg = (f'A CSS file cannot be found for the theme: {theme}.\n'
                   'Please use the --download CLI utility to obtain the CSS file from GitHub.')
            raise FileNotFoundError(msg)
        with open(files[0], encoding='utf-8') as f:
            css = f'<style>{f.read()}</style>'
        return css
