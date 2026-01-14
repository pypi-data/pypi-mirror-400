"""
Enhanced fnmatch with grouping regex and path transformation.

Provides:
- translate(): Enhanced fnmatch.translate() with grouping and ** support
- fnmap(): Transform paths using source and destination patterns

Examples:
    >>> import re
    >>> pattern = translate("**/*.md")
    >>> m = re.match(pattern, "foo/bar/doc.md")
    >>> len(m.groups()) >= 3
    True

    >>> fnmap("foo/bar.md", "**/*.md", "**/*-cn.md")
    'foo/bar-cn.md'
"""

from importlib.metadata import version

__version__ = version("k3fnmatch")

from .fnmatch import (
    translate,
    fnmap,
)

__all__ = [
    "translate",
    "fnmap",
]
