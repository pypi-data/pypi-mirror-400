#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   Project initialisation module.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  n/a

"""

# locals
try:
    from .ghmd import converter
    from .libs._version import __version__
except ImportError:
    from ghmdlib.ghmd import converter
    from ghmdlib.libs._version import __version__

