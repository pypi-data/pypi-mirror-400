#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:Purpose:   Testing module for the ``libs._offline`` module.

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
from ghmdlib.libs._download import Download
from ghmdlib.libs._offline import Offline
from ghmdlib.libs._online import Online


class TestOffline(TestBase):
    """Testing class used to test the ``libs._offline`` module."""

    @classmethod
    def setUpClass(cls):
        """Run this logic at the start of all test cases."""
        testutils.msgs.startoftest(msg='libs._offline')

    def test01a__set_css(self):
        """Test the ``set_css`` method, with missing CSS files.

        :Test:
            - Delete the CSS files from the library.
            - Call the ``Offline.set_css`` method to trigger the
              ``FileNotFoundError``.
            - Download the CSS files.
            - Call the ``Offline.set_css`` method (again) and test for a string to be returned.

        """
        # pylint: disable=protected-access
        for theme in ('dark', 'light'):
            # Build the CSS filepath.
            path = os.path.join(Offline._DIR_RESC,
                                os.path.basename(Online._CSS_URI.format(theme=theme)))
            if os.path.exists(path):
                os.unlink(path)
            self.assertFalse(os.path.exists(path))
        # Test 1: Error raised
        with self.assertRaises(FileNotFoundError):
            Offline.set_css('dark')
        tst1 = Download.download()
        # Test 2: Files found and loaded after download.
        tst2 = Offline.set_css(theme='dark')
        tst3 = Offline.set_css(theme='light')
        self.assertTrue(tst1)
        self.assertIn('<style>', tst2)
        self.assertIn('</style>', tst2)
        self.assertIn('<style>', tst3)
        self.assertIn('</style>', tst3)
        self.assertTrue(len(tst2) > 1000)
        self.assertTrue(len(tst3) > 1000)
