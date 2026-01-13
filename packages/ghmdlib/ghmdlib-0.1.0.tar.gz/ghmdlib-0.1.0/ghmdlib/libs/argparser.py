#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides command line argument parsing
            functionality.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  n/a

"""
# pylint: disable=line-too-long

import argparse
import logging
import os
import sys
# locals
try:
    from ._version import __version__
except ImportError:
    from ghmdlib.libs._version import __version__


class ArgParser:
    """Project command line argument parser."""

    # Program usage and help strings.
    _proj = 'ghmdlib'
    _desc = 'A Markdown to GitHub-style HTML file conversion utility.'
    _vers = __version__
    _h_path = 'Path(s) to the Markdown files to be converted.'
    _h_dark = 'Use a dark HTML theme. (Default)'
    _h_lght = 'Use a light HTML theme.\n\n'
    # Newlines added to provide visual separation.
    _h_down = 'Download the latest CSS files from GitHub. These files are used for offline mode.'
    _h_embd = 'Embed the CSS into the HTML file instead of using the <link> tag.'
    _h_ngfm = 'Use plain Markdown mode instead of GitHub Flavored Markdown (gfm).'
    _h_ofln = ('Keep offline.\n'
               '- Uses cached CSS files and local libraries for the HTML conversion\n'
               '  rather than the GitHub API.')
    _h_prev= 'Auto-open each converted HTML file in a web browser for viewing.\n\n'
    # Newlines added to provide visual separation.
    _h_dbug = 'Display debugging output to the terminal.'
    _h_help = 'Display this help and usage, then exit.'
    _h_vers = 'Display the version, then exit.'

    def __init__(self):
        """Project argument parser class initialiser."""
        self._args = None
        self._epil = f'{self._proj} v{self._vers}'

    @property
    def args(self):
        """Accessor to parsed arguments."""
        return self._args

    def parse(self):
        """Parse command line arguments."""
        argp = argparse.ArgumentParser(prog=self._proj,
                                       description=self._desc,
                                       epilog=self._epil,
                                       formatter_class=argparse.RawTextHelpFormatter,
                                       add_help=False)
        # Order matters here as it affects the display -->
        # If the download utility is called, the PATH is not required.
        if '--download' not in sys.argv:
            argp.add_argument('PATH', help=self._h_path, nargs='+')
        # Themes
        argp.add_argument('--dark', help=self._h_dark, action='store_true')
        argp.add_argument('--light', help=self._h_lght, action='store_true')
        # Options
        argp.add_argument('--download', help=self._h_down, action='store_true')
        argp.add_argument('--embed-css', help=self._h_embd, action='store_true')
        argp.add_argument('--no-gfm', help=self._h_ngfm, action='store_true')
        argp.add_argument('--offline', help=self._h_ofln, action='store_true')
        argp.add_argument('--preview', help=self._h_prev, action='store_true')
        # Other
        argp.add_argument('-d', '--debug', help=self._h_dbug, action='store_true')
        argp.add_argument('-h', '--help', help=self._h_help, action='help')
        argp.add_argument('-V', '--version', help=self._h_vers, action='version', version=self._epil)
        self._args = argp.parse_args()
        self._set_logger()
        try:
            self._verify_args()
            logging.debug('CLI arguments: %s', self._args)
        except ValueError as err:
            argp.print_help()
            print('')
            logging.critical(err)
            print('')
            sys.exit(1)

    def _set_logger(self):
        """Set the debugging level based on the CLI argument.

        The default logging level is set using the ``project.log_level``
        key in ``config.toml``. However, if the ``--debug`` argument is
        passed, the log level is set to 10 (DEBUG).

        :Levels:
            - 10: DEBUG
            - 20: INFO
            - 30: WARNING
            - 40: ERROR
            - 50: CRITICAL

        """
        level = logging.DEBUG if self._args.debug else logging.WARNING
        logging.basicConfig(level=level, format="[%(levelname)s]: %(message)s")

    def _verify_args(self) -> None:
        """Verify the provided arguments are valid.

        If no themes have been selected, the default theme is set to
        dark.

        Raises:
            FileNotFoundError: If any provided PATH does not exist.
            ValueError: If any argument validation fails.

        """
        if not self.args.light:
            self.args.dark = True
        if hasattr(self.args, 'PATH'):  # Only required if not --download
            for file in self.args.PATH:
                if not os.path.exists(file):
                    msg = f'The following file cannot be found: {file}'
                    raise FileNotFoundError(msg)
                if not os.path.splitext(file)[1].lower() == '.md':
                    msg = 'All files are expected to have a Markdown (.md or .MD) file extension.'
                    raise ValueError(msg)


# Make the arg parser accessible as an import.
argparser = ArgParser()
