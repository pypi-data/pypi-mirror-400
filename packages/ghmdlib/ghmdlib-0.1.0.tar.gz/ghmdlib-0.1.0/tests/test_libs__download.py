#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:Purpose:   Testing module for the ``libs._download`` module.

:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  n/a

"""
# pylint: disable=import-error

import hashlib
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


class TestDownload(TestBase):
    """Testing class used to test the ``libs._download`` module."""

    @classmethod
    def setUpClass(cls):
        """Run this logic at the start of all test cases."""
        testutils.msgs.startoftest(msg='libs._download')

    def test01a__download(self):
        """Test the ``download`` method.

        :Test:
            - Download the CSS files manually (via the ``_online``
              module) and store the hash from the downloaded CSS data.
            - Call the ``download`` method and verify the content of the
              downloaded CSS files matches the expected hash.

        """
        # pylint: disable=protected-access
        for theme in ('dark', 'light'):
            with self.subTest(msg=f'{theme=}'):
                css = Online.set_css(theme=theme, embed_css=True, raw=True)
                exp2 = hashlib.md5(css.encode()).hexdigest()
                tst1 = Download.download()
                # Build filepath for verification.
                path = os.path.join(Offline._DIR_RESC,
                                    os.path.basename(Online._CSS_URI.format(theme=theme)))
                tst2 = self.get_checksum(path=path)
                self.assertTrue(tst1)
                self.assertEqual(exp2, tst2)
