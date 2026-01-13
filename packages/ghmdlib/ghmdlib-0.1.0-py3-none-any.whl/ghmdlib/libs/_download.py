#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides the functionality for the ``--download``
            CLI utility.

            The download utility is used to refresh the local CSS files
            by downloading the latest from GitHub.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  This module is designed for internal use only.

"""

import logging
import os
# locals
try:
    from ._offline import Offline
    from ._online import Online
except ImportError:
    from ghmdlib.libs._online import Online
    from ghmdlib.libs._offline import Offline

logger = logging.getLogger(__name__)

# TODO: Move the constants (accessed by the imports) to a config (or constants) file.


class Download:
    """Implementation for the CSS file refresh utillity."""

    @classmethod
    def download(cls) -> bool:
        """Download the latest CSS files from GitHub.

        This method downloads both the 'dark' and 'light' themes and
        stores them in the local library's ``resources`` directory.

        Returns:
            bool: True if both files were downloaded successfully,
            otherwise False.

        """
        # pylint: disable=protected-access  # Can be removed once the config file is ready.
        files = []
        themes = ('dark', 'light')
        for theme in themes:
            logging.debug('Downloading CSS theme: %s', theme)
            if ( css := Online.set_css(theme=theme, embed_css=True, raw=True) ):
                path = os.path.join(Offline._DIR_RESC,
                                    os.path.basename(Online._CSS_URI.format(theme=theme)))
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(css)
                    files.append(path)
        return all(map(os.path.exists, files))
