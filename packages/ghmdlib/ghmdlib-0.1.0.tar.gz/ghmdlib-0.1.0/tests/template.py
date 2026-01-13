#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:Purpose:   Testing module for the ``module`` module.

:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  n/a

# pylint: disable=import-error
# pylint: disable=invalid-name
# pylint: disable=wrong-import-order
"""

try:
    from .base import TestBase
    from .testlibs.testutils import testutils
except ImportError:
    from base import TestBase
    from testlibs.testutils import testutils
# The imports for <project> must be after TestBase.
# from <project> import <module>


class TestModule(TestBase):
    """Testing class used to test the ``module`` module."""

    @classmethod
    def setUpClass(cls):
        """Run this logic at the start of all test cases."""
        testutils.msgs.startoftest(msg='')

    # def setUp(self):
    #     """Run this logic *before* each test case."""
    #     self.disable_terminal_output()

    # def tearDown(self):
    #     """Run this logic *after* each test case."""
    #     self.enable_terminal_output()

    def test01a__methodname(self):
        """Test the ``method`` method.

        :Test:
            - How this test operates ...

        """
        # inp = []
        # exp = []
        # for i, e in zip(inp, exp):
            # test = <method_call>(i)
            # utilities.assert_true(expected=e, test=test, msg=self._MSG1)
