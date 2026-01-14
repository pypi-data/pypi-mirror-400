from __future__ import annotations

import re
from typing import Any


def translate(pat: str) -> str:
    """Translate a shell PATTERN to a regular expression with grouping.

    Enhanced version of fnmatch.translate() that:
    - Produces grouping regex for capturing matched segments
    - Supports ** for multi-segment matching (matches across /)
    - Supports * for single-segment matching (no /)
    - Supports ? for single character
    - Supports [...] for character classes
    - Supports backslash escaping: \\*, \\?, \\[, \\], \\\\

    Args:
        pat: Shell pattern with wildcards

    Returns:
        Regular expression string with capture groups

    Examples:
        >>> import re
        >>> pattern = translate("**/*.md")
        >>> m = re.match(pattern, "foo/bar/doc.md")
        >>> m.groups()
        ('', 'foo/bar', '/', 'doc', '.md')

        >>> pattern = translate("*.txt")
        >>> bool(re.match(pattern, "file.txt"))
        True
        >>> bool(re.match(pattern, "dir/file.txt"))
        False

        >>> pattern = translate(r"file\\*.txt")
        >>> bool(re.match(pattern, "file*.txt"))
        True
    """
    # Sentinel objects for star types
    STAR: Any = object()  # "*" - single segment
    STAR2: Any = object()  # "**" - multi segment

    def is_star(v: Any) -> bool:
        return v is STAR or v is STAR2

    def star_to_regex(v: Any) -> str:
        # match single path segment, contains no `/`, escaped `\/` is allowed,
        # double escaped is not allowed: `\\/`
        if v is STAR:
            return r"((?:[^/\\]|\\/|\\\\)*?)"

        # match multi path segment
        if v is STAR2:
            return r"(.*?)"

        raise ValueError(f"not star: {v!r}")

    res: list[str | Any] = []
    add = res.append
    i, n = 0, len(pat)
    while i < n:
        c = pat[i]
        i = i + 1

        # Handle backslash escaping
        if c == "\\":
            if i < n:
                next_char = pat[i]
                # Escape special characters: * ? [ ] \
                if next_char in "*?[]\\":
                    # Add the escaped character as a literal regex-escaped string
                    add(re.escape(next_char))
                    i = i + 1
                    continue
                # Not a special char, treat backslash as literal
                add(re.escape(c))
            else:
                # Trailing backslash - treat as literal
                add(re.escape(c))
        elif c == "*":
            add(STAR)

            # compress "**", "**..." to "**"
            if len(res) >= 2:
                if res[-1] is STAR:
                    if res[-2] is STAR or res[-2] is STAR2:
                        res.pop()
                        res[-1] = STAR2
        elif c == "?":
            add(".")
        elif c == "[":
            j = i
            if j < n and pat[j] == "!":
                j = j + 1
            if j < n and pat[j] == "]":
                j = j + 1
            while j < n and pat[j] != "]":
                j = j + 1
            if j >= n:
                add("\\[")
            else:
                stuff = pat[i:j]
                if "-" not in stuff:
                    stuff = stuff.replace("\\", r"\\")
                else:
                    chunks: list[str] = []
                    k = i + 2 if pat[i] == "!" else i + 1
                    while True:
                        k = pat.find("-", k, j)
                        if k < 0:
                            break
                        chunks.append(pat[i:k])
                        i = k + 1
                        k = k + 3
                    chunk = pat[i:j]
                    if chunk:
                        chunks.append(chunk)
                    else:
                        chunks[-1] += "-"
                    # Remove empty ranges -- invalid in RE.
                    for k in range(len(chunks) - 1, 0, -1):
                        if chunks[k - 1][-1] > chunks[k][0]:
                            chunks[k - 1] = chunks[k - 1][:-1] + chunks[k][1:]
                            del chunks[k]
                    # Escape backslashes and hyphens for set difference (--).
                    # Hyphens that create ranges shouldn't be escaped.
                    stuff = "-".join(s.replace("\\", r"\\").replace("-", r"\-") for s in chunks)
                # Escape set operations (&&, ~~ and ||).
                stuff = re.sub(r"([&~|])", r"\\\1", stuff)
                i = j + 1
                if not stuff:
                    # Empty range: never match.
                    add("(?!)")
                elif stuff == "!":
                    # Negated empty range: match any character.
                    add(".")
                else:
                    if stuff[0] == "!":
                        stuff = "^" + stuff[1:]
                    elif stuff[0] in ("^", "["):
                        stuff = "\\" + stuff
                    add(f"[{stuff}]")
        else:
            add(re.escape(c))
    assert i == n

    # Deal with STARs.
    inp = res

    res = []
    add = res.append

    i, n = 0, len(inp)
    # Fixed pieces at the start?
    add("(")
    while i < n and not is_star(inp[i]):
        add(inp[i])
        i += 1
    add(")")

    # Now deal with STAR fixed STAR fixed ...
    # For an interior `STAR fixed` pairing, we want to do a minimal
    # .*? match followed by `fixed`, with no possibility of backtracking.
    # Atomic groups ("(?>...)") allow us to spell that directly.
    # Note: people rely on the undocumented ability to join multiple
    # translate() results together via "|" to build large regexps matching
    # "one of many" shell patterns.

    while i < n:
        assert is_star(inp[i])

        star = inp[i]
        i += 1

        if i < n:
            assert not is_star(inp[i])

        fixed: list[str] = []
        while i < n and not is_star(inp[i]):
            fixed.append(inp[i])
            i += 1

        fixed_str = "".join(fixed)

        if fixed_str == "":
            add(star_to_regex(star))
        else:
            add(star_to_regex(star))
            add("(" + fixed_str + ")")

    assert i == n
    res_str = "".join(res)
    return rf"(?s:{res_str})\Z"


def fnmap(src_path: str, src_pattern: str, dst_pattern: str) -> str:
    """Transform a path using source and destination patterns.

    Matches src_path against src_pattern, extracts the wildcard segments,
    and reconstructs using dst_pattern with the same wildcards in corresponding
    positions.

    Args:
        src_path: Path to transform (e.g., "foo/x/y.md")
        src_pattern: Source pattern with wildcards (e.g., "**/*.md")
        dst_pattern: Destination pattern with wildcards (e.g., "**/*-cn.md")

    Returns:
        Transformed path (e.g., "foo/x/y-cn.md")

    Examples:
        >>> fnmap("foo/x/y.md", "**/*.md", "**/*-cn.md")
        'foo/x/y-cn.md'

        >>> fnmap("a/b/c.txt", "*/*/*.txt", "*/*/*-backup.txt")
        'a/b/c-backup.txt'

        >>> fnmap("file.md", "*.md", "*-backup.md")
        'file-backup.md'
    """
    regex = translate(src_pattern)

    dst_parts = re.split(r"([*]+)", dst_pattern)

    src_parts = re.split(regex, src_path)

    # strip two empty string produced.
    src_parts = src_parts[1:-1]

    #  (?s:(foo/)(?>(.*?)(/d/))(.*)(\.md))\Z
    #  src_parts:     ['foo/', 'x/y/z', '/d/', 'bar', '.md']
    #  dst_parts: ['bar/', '**', '/d/', '*', '.cn.md']
    #
    #  Replace non-wildcard part with the corresponding one in the dst_parts

    res: list[str] = []
    for i, p in enumerate(src_parts):
        if dst_parts[i] in ("**", "*"):
            res.append(p)
        else:
            res.append(dst_parts[i])

    return "".join(res)
