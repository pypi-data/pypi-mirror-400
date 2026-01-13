"""
mdx_better_lists
~~~~~~~~~~~~~~~~

A Python-Markdown extension for better list handling.

:copyright: (c) 2025 by mdx_better_lists contributors
:license: MIT, see LICENSE for more details.
"""

__version__ = "1.0.0"

from .extension import BetterListsExtension


def makeExtension(**kwargs):
    """Create and return an instance of the extension."""
    return BetterListsExtension(**kwargs)
