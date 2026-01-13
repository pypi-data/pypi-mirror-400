#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides the superclass which is to be inherited
            by the test-specific modules.

:Platform:  Linux/Windows | Python 3.6+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Reminder:  The testing suite must **not** be deployed into production
            as it contains sensitive information for the development
            environment.

:Example:
    Example code use::

        # Run all tests via the shell script.
        ./run.sh

        # Run all tests using unittest.
        python -m unittest discover

        # Run a single test.
        python -m unittest test_search.py

"""
# pylint: disable=wrong-import-position

import hashlib
import os
import re
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import unittest
import warnings


class TestBase(unittest.TestCase):
    """Private generalised base-testing class.

    This class is designed to be inherited by each test-specific class.

    """

    _DIR_ROOT = os.path.realpath(os.path.dirname(__file__))
    _DIR_RESC = os.path.join(_DIR_ROOT, 'resources')
    _DIR_DATA = os.path.join(_DIR_RESC, 'data')
    _DIR_FILES = os.path.join(_DIR_RESC, 'files')
    _DIR_FILES_MD = os.path.join(_DIR_FILES, 'md')
    _PATH_ACCESS = '/var/devmt/access_tokens/github/ghmdlib-testing'

    @classmethod
    def setUpClass(cls):
        """Setup the testing class once, for all tests."""

    @classmethod
    def tearDownClass(cls):
        """Teardown the testing class once all tests are complete."""

    @staticmethod
    def get_checksum(path: str, remove_data_run_id: bool=False) -> str:
        """Calculate the MD5 checksum for a given file.

        Args:
            path (str): Full path to the file to be checksummed.
            remove_data_run_id (bool, optional): When the GitHub API math
                renderer is used, a ``data_run_id`` tag is placed in the
                HTML which includes a dynamic hash string. This must be
                removed for checksum comparisons. Defaults to False.

        Returns:
            str: A string containing the MD5 checksum for the given file.

        """
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            if remove_data_run_id:
                # beautifulsoup is not used to keep dependencies to a minimum.
                content = re.sub('data-run-id="(.*)"', 'data-run-id="[REMOVED]"', content)
        return hashlib.md5(content.encode()).hexdigest()

    @classmethod
    def ignore_warnings(cls):
        """Ignore (spurious) warnings for methods under test."""

    # def read_pickle(self, module: str, method: str) -> object:
    #     """Read the named pickle file.

    #     Args:
    #         module (str): Name of the module (as this is the path).
    #         method (str): Name of the caller method (as this is the filename).

    #     Returns:
    #         object: An object containing the contents of the serialised
    #         file.

    #     """
    #     path = os.path.join(self._DIR_DATA, module, f'{method}.p')
    #     with open(path, 'rb') as f:
    #         data = pickle.load(f)
    #     return data

    @classmethod
    def reset_warnings(cls):
        """Reset warnings which have been ignored."""
        warnings.resetwarnings()
