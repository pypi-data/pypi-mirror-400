# k3fnmatch

[![Action-CI](https://github.com/pykit3/k3fnmatch/actions/workflows/python-package.yml/badge.svg)](https://github.com/pykit3/k3fnmatch/actions/workflows/python-package.yml)
[![Documentation Status](https://readthedocs.org/projects/k3fnmatch/badge/?version=stable)](https://k3fnmatch.readthedocs.io/en/stable/?badge=stable)
[![Package](https://img.shields.io/pypi/pyversions/k3fnmatch)](https://pypi.org/project/k3fnmatch)

Enhanced fnmatch with grouping regex and path transformation

k3fnmatch is a component of [pykit3] project: a python3 toolkit set.


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



# Install

```
pip install k3fnmatch
```

# Synopsis

```python
>>> import re
>>> pattern = translate("**/*.md")
>>> m = re.match(pattern, "foo/bar/doc.md")
>>> len(m.groups()) >= 3
True
>>> fnmap("foo/bar.md", "**/*.md", "**/*-cn.md")
'foo/bar-cn.md'
```

#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>


[pykit3]: https://github.com/pykit3