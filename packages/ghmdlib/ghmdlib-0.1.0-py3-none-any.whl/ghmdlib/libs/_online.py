#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides the functionality for **online**
            conversions.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  This module is designed for internal use only.

"""
# pylint: disable=line-too-long  # _CSS_URI and _CSS_LINK (only)

import json
import logging
import requests

logger = logging.getLogger(__name__)


class Online:
    """This class provides the functions used for online conversions.

    Specifically, this class employs requests to GitHub to obtain the
    CSS and calls to the GitHub API for Markdown conversion.

    """

    _CSS_LINK = '<link rel=\"stylesheet\" href=\"{uri}\" crossorigin=\"anonymous\" referrerpolicy=\"no-referrer\" />'
    _CSS_URI = 'https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.8.1/github-markdown-{theme}.min.css'
    _TIMEOUT = 5

    @classmethod
    def convert(cls, content: str, headers: str, mode: str) -> str:
        """Convert Markdown file(s) to HTML.

        Args:
            content (str): Markdown file content to be converted.
            headers (str): Headers to be send in the HTTP request.
            mode (str): Mode to be used for the conversion.

        Returns:
            str: A string containing the Markdown content converted to
            HTML.

        """
        resp = requests.post('https://api.github.com/markdown',
                             headers=headers,
                             data=json.dumps({'text': content, 'mode': mode}),
                             timeout=cls._TIMEOUT)
        logger.debug('API response: %s', resp)
        if resp.status_code != 200:  # nocover
            msg = 'An error occurred while converting through the GitHub API.'
            raise RuntimeError(msg)
        return resp.text

    @classmethod
    def set_css(cls, theme: str, embed_css: bool, raw: bool=False) -> str:
        """Get and set the CSS for the HTML output.

        Args:
            theme (str): Theme to be used (dark | light).
            embed_css (bool): Embed the CSS rather than linking.
            raw (bool, optional): Return the raw CSS content, as
                downloaded. This *excludes* the ``<style>`` tag wrapper.
                Defaults to False.

        Raises:
            ValueError: If the CSS could not be retrieved.

        Returns:
            str: A string containing either the CSS for the desired
            theme, or a link; depending on whether the ``embed_css``
            argument is True or False, respectively.

        """
        css_uri = cls._CSS_URI.format(theme=theme)
        if embed_css:
            resp = requests.get(css_uri, timeout=cls._TIMEOUT)
            if resp.status_code != 200:  # nocover
                msg = ('Could not retrieve CSS. Check your internet connection or try without '
                       '--embed-css.')
                raise RuntimeError(msg)
            css = f'<style>{resp.text}</style>' if not raw else resp.text
        else:
            css = cls._CSS_LINK.format(uri=css_uri)
        return css
