#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:Purpose:   Testing module for the ``ghmd`` module.

:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  n/a

"""
# pylint: disable=import-error

import os
try:
    from .base import TestBase
    from .testlibs.testutils import testutils
except ImportError:
    from base import TestBase
    from testlibs.testutils import testutils
# The imports for <project> must be after TestBase.
from ghmdlib import converter


class TestGHMD(TestBase):
    """Testing class used to test the ``ghmd`` module."""

    _ATTN_H = os.path.join(TestBase._DIR_FILES_MD, 'attention-is-all-you-need.html')
    _ATTN_M = os.path.join(TestBase._DIR_FILES_MD, 'attention-is-all-you-need.md')
    _DOCL_H = os.path.join(TestBase._DIR_FILES_MD, 'docling-technical-report.html')
    _DOCL_M = os.path.join(TestBase._DIR_FILES_MD, 'docling-technical-report.md')
    _LOR1_H = os.path.join(TestBase._DIR_FILES_MD, 'lorem-ipsum-1-tagged-headings.html')
    _LOR1_M = os.path.join(TestBase._DIR_FILES_MD, 'lorem-ipsum-1-tagged-headings.md')
    _LOR2_H = os.path.join(TestBase._DIR_FILES_MD, 'lorem-ipsum-2-tagged-headings.html')
    _LOR2_M = os.path.join(TestBase._DIR_FILES_MD, 'lorem-ipsum-2-tagged-headings.md')
    _THEMES = ('dark', 'light')

    @classmethod
    def setUpClass(cls):
        """Run this logic at the start of all test cases."""
        testutils.msgs.startoftest(msg='ghmd')

    # def setUp(self):
    #     """Run this logic *before* each test case."""
    #     self.disable_terminal_output()

    # def tearDown(self):
    #     """Run this logic *after* each test case."""
    #     self.enable_terminal_output()

    def test01a__blackbox(self):
        """Test the ``ghmdlib`` library as a blackbox.

        :Test:
            - Verify the provided Markdown file is converted as expected.

        """
        md = self._ATTN_M
        html = self._ATTN_H
        hashes = ('38b1855fd00211ea206f30510fca384b', '74fe873f508637810511b36418d4c37b')
        for theme, hash_ in zip(self._THEMES, hashes):
            tst1 = converter.convert(path=md,
                                     theme=theme,
                                     embed_css=False,
                                     no_gfm=False,
                                     offline=False,
                                     preview=False)
            tst2 = self.get_checksum(path=html, remove_data_run_id=True)
            self.assertTrue(tst1)
            self.assertEqual(hash_, tst2)

    def test01b__blackbox(self):
        """Test the ``ghmdlib`` library as a blackbox.

        :Test:
            - Verify the provided Markdown file is converted as expected.

        """
        md = self._DOCL_M
        html = self._DOCL_H
        hashes = ('77543a66414aea13a8e4b6f6e4e524f8', '915cabc10c2c444902ca63caaf9279d0')
        for theme, hash_ in zip(self._THEMES, hashes):
            tst1 = converter.convert(path=md,
                                     theme=theme,
                                     embed_css=True,  # <-- Changed
                                     no_gfm=False,
                                     offline=False,
                                     preview=False)
            tst2 = self.get_checksum(path=html, remove_data_run_id=False)
            self.assertTrue(tst1)
            self.assertEqual(hash_, tst2)

    def test01c__blackbox(self):
        """Test the ``ghmdlib`` library as a blackbox.

        :Test:
            - Verify the provided Markdown file is converted as expected.

        """
        md = self._LOR1_M
        html = self._LOR1_H
        hashes = ('91cf0a0228ac3278ade7129a2b533c95', 'a783bf59328d46c21ba31abc9842c327')
        for theme, hash_ in zip(self._THEMES, hashes):
            tst1 = converter.convert(path=md,
                                     theme=theme,
                                     embed_css=False,
                                     no_gfm=True,  # <-- Changed
                                     offline=False,
                                     preview=False)
            tst2 = self.get_checksum(path=html, remove_data_run_id=False)
            self.assertTrue(tst1)
            self.assertEqual(hash_, tst2)

    def test01d__blackbox(self):
        """Test the ``ghmdlib`` library as a blackbox.

        :Test:
            - Verify the provided Markdown file is converted as expected.

        """
        md = self._LOR2_M
        html = self._LOR2_H
        hashes = ('33208dd3608e94cd24c5c2fdb491e869', '695346f2dda79a6b4221ce04efeb03dd')
        for theme, hash_ in zip(self._THEMES, hashes):
            tst1 = converter.convert(path=md,
                                     theme=theme,
                                     embed_css=False,
                                     no_gfm=False,
                                     offline=True,  # <-- Changed
                                     preview=False)
            tst2 = self.get_checksum(path=html, remove_data_run_id=False)
            self.assertTrue(tst1)
            self.assertEqual(hash_, tst2)

    def test01e__blackbox(self):
        """Test the ``ghmdlib`` library as a blackbox.

        :Test:
            - Verify the provided Markdown file is converted as expected.
            - This test uses the GITHUB_TOKEN environment variable to
              test the GitHub API with an access token.

        """
        if not os.path.exists(self._PATH_ACCESS):
            self.skipTest(reason='GitHub token file not found.')
        with open(self._PATH_ACCESS, 'r', encoding='ascii') as f:
            var, token = f.read().split('=')
            token = token.strip()
        os.environ[var] = token
        md = self._LOR2_M
        html = self._LOR2_H
        hashes = ('b190ff31429630733b88b33a82e325c9', 'c4b5db8cb014b8e10847cb7b48ab01db')
        for theme, hash_ in zip(self._THEMES, hashes):
            tst1 = converter.convert(path=md,
                                     theme=theme,
                                     embed_css=False,
                                     no_gfm=False,
                                     offline=False,
                                     preview=False)
            tst2 = self.get_checksum(path=html, remove_data_run_id=False)
            self.assertTrue(tst1)
            self.assertEqual(hash_, tst2)
