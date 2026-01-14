#!/usr/bin/env python
# coding: utf-8

import re
import unittest

import k3fnmatch


class TestTranslate(unittest.TestCase):
    """Test translate() function with various patterns"""

    def test_simple_star(self):
        """Test single * wildcard"""
        cases = [
            ("*.txt", "file.txt", True),
            ("*.txt", "dir/file.txt", False),
            ("*.txt", "file.md", False),
        ]
        for pattern, path, should_match in cases:
            regex = k3fnmatch.translate(pattern)
            matches = re.match(regex, path) is not None
            self.assertEqual(matches, should_match, f"Pattern {pattern} vs {path}")

    def test_double_star(self):
        """Test ** for multi-segment matching"""
        cases = [
            ("**/*.md", "foo/bar/doc.md", True),
            ("**/*.md", "foo/doc.md", True),
            ("**/*.md", "a/b/c/d.md", True),
            ("**/*.md", "no-match.txt", False),
            # ** requires at least one /, so "doc.md" without prefix doesn't match
            ("**/*.md", "doc.md", False),
        ]
        for pattern, path, should_match in cases:
            regex = k3fnmatch.translate(pattern)
            matches = re.match(regex, path) is not None
            self.assertEqual(matches, should_match)

    def test_question_mark(self):
        """Test ? for single character"""
        cases = [
            ("file?.txt", "file1.txt", True),
            ("file?.txt", "fileA.txt", True),
            ("file?.txt", "file.txt", False),
            ("file?.txt", "file12.txt", False),
        ]
        for pattern, path, should_match in cases:
            regex = k3fnmatch.translate(pattern)
            matches = re.match(regex, path) is not None
            self.assertEqual(matches, should_match)

    def test_character_class(self):
        """Test [...] character classes"""
        cases = [
            ("file[123].txt", "file1.txt", True),
            ("file[123].txt", "file4.txt", False),
            ("file[a-z].txt", "filex.txt", True),
            ("file[!0-9].txt", "filea.txt", True),
            ("file[!0-9].txt", "file5.txt", False),
        ]
        for pattern, path, should_match in cases:
            regex = k3fnmatch.translate(pattern)
            matches = re.match(regex, path) is not None
            self.assertEqual(matches, should_match)

    def test_grouping_capture(self):
        """Test that regex produces capture groups"""
        pattern = "**/*.md"
        regex = k3fnmatch.translate(pattern)
        m = re.match(regex, "foo/bar/doc.md")
        self.assertIsNotNone(m)
        groups = m.groups()
        # Pattern **/*.md produces 5 groups: ('', multi-segment, '/', single-segment, '.md')
        self.assertEqual(len(groups), 5)
        # Verify key captured segments
        self.assertEqual(groups[0], "")  # Empty prefix before **
        self.assertEqual(groups[1], "foo/bar")  # Multi-segment match
        self.assertEqual(groups[2], "/")  # Separator
        self.assertEqual(groups[3], "doc")  # Filename
        self.assertEqual(groups[4], ".md")  # Extension

    def test_escaped_chars(self):
        """Test escaping special characters"""
        cases = [
            ("file.txt", "file.txt", True),
            ("file.txt", "filetxt", False),
            # [1] is a character class matching '1'
            ("file[1].txt", "file1.txt", True),
            ("file[1].txt", "file[1].txt", False),
        ]
        for pattern, path, should_match in cases:
            regex = k3fnmatch.translate(pattern)
            matches = re.match(regex, path) is not None
            self.assertEqual(matches, should_match)

    def test_consecutive_stars(self):
        """Test that *** compresses to **"""
        regex1 = k3fnmatch.translate("**/*.txt")
        regex2 = k3fnmatch.translate("***/*.txt")
        regex3 = k3fnmatch.translate("****/*.txt")
        self.assertEqual(regex1, regex2)
        self.assertEqual(regex1, regex3)

    def test_regex_format(self):
        """Test exact regex output format from original test suite"""
        # Test simple * pattern
        self.assertEqual(
            r"(?s:(foo/)((?:[^/\\]|\\/|\\\\)*?)(\.md))\Z",
            k3fnmatch.translate(r"foo/*.md"),
        )

        # Test ** pattern
        self.assertEqual(
            r"(?s:(foo/)(.*?)(/)((?:[^/\\]|\\/|\\\\)*?)(\.md))\Z",
            k3fnmatch.translate(r"foo/**/*.md"),
        )

        # Test ** with fixed middle segment
        self.assertEqual(
            r"(?s:(foo/)(.*?)(/d/)((?:[^/\\]|\\/|\\\\)*?)(\.md))\Z",
            k3fnmatch.translate(r"foo/**/d/*.md"),
        )


class TestFnmap(unittest.TestCase):
    """Test fnmap() path transformation"""

    def test_basic_transformation(self):
        """Test simple path transformation"""
        cases = [
            ("foo/x/y.md", "**/*.md", "**/*-cn.md", "foo/x/y-cn.md"),
            ("a/b.txt", "*/*.txt", "*/*.log", "a/b.log"),
            ("file.md", "*.md", "*-backup.md", "file-backup.md"),
        ]
        for src, src_pat, dst_pat, expected in cases:
            result = k3fnmatch.fnmap(src, src_pat, dst_pat)
            self.assertEqual(result, expected, f"{src} + {src_pat} → {dst_pat}")

    def test_multiple_wildcards(self):
        """Test multiple wildcards in pattern"""
        result = k3fnmatch.fnmap("docs/guide/intro.md", "*/*/*.md", "*/*/*.html")
        self.assertEqual(result, "docs/guide/intro.html")

    def test_star_with_single_char(self):
        """Test * matching single character"""
        # Use * for both src and dst patterns
        result = k3fnmatch.fnmap("file1.txt", "file*.txt", "file*-new.txt")
        self.assertEqual(result, "file1-new.txt")

    def test_mixed_wildcards(self):
        """Test mixing ** and * wildcards"""
        result = k3fnmatch.fnmap("src/foo/bar/test.py", "src/**/*.py", "dist/**/*.js")
        self.assertEqual(result, "dist/foo/bar/test.js")

    def test_no_wildcards(self):
        """Test pattern without wildcards"""
        result = k3fnmatch.fnmap("file.txt", "file.txt", "newfile.txt")
        self.assertEqual(result, "newfile.txt")

    def test_original_md2zhihu_cases(self):
        """Test cases from original md2zhihu test suite"""
        src = r"foo/x/y/z/d/bar.md"

        # Replace prefix: foo -> bar
        self.assertEqual(
            r"bar/x/y/z/d/bar.cn.md",
            k3fnmatch.fnmap(src, r"foo/**/*.md", r"bar/**/*.cn.md"),
        )

        # Match with fixed middle segment /d/
        self.assertEqual(
            r"bar/x/y/z/d/bar.cn.md",
            k3fnmatch.fnmap(src, r"foo/**/d/*.md", r"bar/**/d/*.cn.md"),
        )

        # Insert new segment /f/ in destination
        self.assertEqual(
            r"bar/x/y/z/d/f/bar.cn.md",
            k3fnmatch.fnmap(src, r"foo/**/*.md", r"bar/**/f/*.cn.md"),
        )


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""

    def test_empty_pattern(self):
        """Test empty pattern"""
        regex = k3fnmatch.translate("")
        self.assertTrue(re.match(regex, ""))
        self.assertFalse(re.match(regex, "anything"))

    def test_pattern_with_backslash(self):
        """Test patterns with escaped backslashes"""
        pattern = "*"
        regex = k3fnmatch.translate(pattern)
        # Should match paths with escaped slashes
        self.assertTrue(re.match(regex, "file"))

    def test_star_at_boundaries(self):
        """Test * at start/end of pattern"""
        cases = [
            ("*", "anything", True),
            ("*.txt", "file.txt", True),
            ("prefix*", "prefixsuffix", True),
        ]
        for pattern, path, should_match in cases:
            regex = k3fnmatch.translate(pattern)
            matches = re.match(regex, path) is not None
            self.assertEqual(matches, should_match)


class TestBackslashEscaping(unittest.TestCase):
    """Test backslash escaping of special characters"""

    def test_escaped_star(self):
        """\\* should match literal asterisk"""
        pattern = k3fnmatch.translate(r"file\*.txt")
        self.assertTrue(re.match(pattern, "file*.txt"))
        self.assertFalse(re.match(pattern, "fileABC.txt"))

    def test_escaped_question_mark(self):
        """\\? should match literal question mark"""
        pattern = k3fnmatch.translate(r"file\?.txt")
        self.assertTrue(re.match(pattern, "file?.txt"))
        self.assertFalse(re.match(pattern, "filea.txt"))

    def test_escaped_brackets(self):
        """\\[1\\] should match literal [1]"""
        pattern = k3fnmatch.translate(r"file\[1\].txt")
        self.assertTrue(re.match(pattern, "file[1].txt"))
        self.assertFalse(re.match(pattern, "file1.txt"))

    def test_double_backslash(self):
        """\\\\\\\ represents escaped backslash"""
        pattern = k3fnmatch.translate(r"file\\name.txt")
        self.assertTrue(re.match(pattern, r"file\name.txt"))

    def test_windows_path_pattern(self):
        """C:\\\\path\\\\*.txt for Windows paths"""
        pattern = k3fnmatch.translate(r"C:\\Users\\*.txt")
        self.assertTrue(re.match(pattern, r"C:\Users\file.txt"))
        self.assertFalse(re.match(pattern, r"C:\Users\sub\file.txt"))

    def test_backslash_before_non_special(self):
        """Backslash before non-special char is treated as literal backslash"""
        pattern = k3fnmatch.translate(r"a\b.txt")
        # \b is not an escape sequence, so it matches literal backslash + b
        self.assertTrue(re.match(pattern, r"a\b.txt"))
        self.assertFalse(re.match(pattern, "ab.txt"))

    def test_trailing_backslash(self):
        """Pattern ending with backslash"""
        pattern = k3fnmatch.translate(r"file\\")
        self.assertTrue(re.match(pattern, "file\\"))

    def test_mixed_escaped_and_wildcard(self):
        """Mix of escaped and unescaped wildcards"""
        # \* is literal asterisk, then * is wildcard
        pattern = k3fnmatch.translate(r"file\**")
        self.assertTrue(re.match(pattern, "file*test"))
        self.assertTrue(re.match(pattern, "file*"))
        self.assertFalse(re.match(pattern, "filetest"))


class TestFnmapEdgeCases(unittest.TestCase):
    """Test fnmap edge cases and error conditions"""

    def test_path_not_matching_pattern(self):
        """Path that doesn't match source pattern returns empty"""
        src = "completely/different/path.txt"
        # When path doesn't match, fnmap returns empty string
        result = k3fnmatch.fnmap(src, "foo/**/*.md", "bar/**/*.html")
        self.assertEqual(result, "")

    def test_empty_path_and_pattern(self):
        """Empty path and pattern"""
        result = k3fnmatch.fnmap("", "", "")
        self.assertEqual(result, "")

    def test_inserting_fixed_segments(self):
        """Insert fixed segments in destination"""
        src = "foo/bar.md"
        result = k3fnmatch.fnmap(src, "foo/*.md", "dist/output/*-final.html")
        self.assertEqual(result, "dist/output/bar-final.html")

    def test_fnmap_with_only_single_star(self):
        """Pattern with only a single star"""
        src = "anything.txt"
        result = k3fnmatch.fnmap(src, "*.txt", "*-copy.txt")
        self.assertEqual(result, "anything-copy.txt")

    def test_multiple_directory_levels(self):
        """Transform paths with multiple directory levels"""
        src = "a/b/c/d/e.txt"
        result = k3fnmatch.fnmap(src, "a/**/*.txt", "z/**/*.log")
        self.assertEqual(result, "z/b/c/d/e.log")

    def test_rearrange_path_components(self):
        """Change order of path components using multiple patterns"""
        src = "docs/api/function.md"
        result = k3fnmatch.fnmap(src, "docs/*/*.md", "web/*/*.html")
        self.assertEqual(result, "web/api/function.html")

    def test_mixed_fixed_and_wildcard_transformation(self):
        """Mix of fixed text and wildcards in both patterns"""
        src = "project-v2/src/main.py"
        result = k3fnmatch.fnmap(src, "project-v2/src/*.py", "project-v3/dist/*.js")
        self.assertEqual(result, "project-v3/dist/main.js")

    def test_consecutive_wildcards_in_pattern(self):
        """Pattern with consecutive star wildcards"""
        src = "a/b.txt"
        result = k3fnmatch.fnmap(src, "*/*.txt", "*/*-new.txt")
        self.assertEqual(result, "a/b-new.txt")


class TestCharacterClassEdgeCases(unittest.TestCase):
    """Test character class edge cases

    Note: Like Python's standard fnmatch, k3fnmatch does not support:
    - Backslash escaping within character classes (e.g., [a\]b])
    - Empty negated classes (e.g., [!])
    These limitations are consistent with fnmatch behavior.
    """

    def test_empty_character_class(self):
        """Empty class should not match anything"""
        pattern = k3fnmatch.translate("file[].txt")
        self.assertFalse(re.match(pattern, "file.txt"))
        self.assertFalse(re.match(pattern, "filea.txt"))

    def test_dash_at_start_of_class(self):
        """[-abc] matches -, a, b, or c"""
        pattern = k3fnmatch.translate("file[-abc].txt")
        self.assertTrue(re.match(pattern, "file-.txt"))
        self.assertTrue(re.match(pattern, "filea.txt"))
        self.assertFalse(re.match(pattern, "filed.txt"))

    def test_dash_at_end_of_class(self):
        """[abc-] matches a, b, c, or -"""
        pattern = k3fnmatch.translate("file[abc-].txt")
        self.assertTrue(re.match(pattern, "file-.txt"))
        self.assertTrue(re.match(pattern, "fileb.txt"))

    def test_multiple_ranges_in_class(self):
        """[a-zA-Z0-9] for alphanumeric"""
        pattern = k3fnmatch.translate("file[a-zA-Z0-9].txt")
        self.assertTrue(re.match(pattern, "filea.txt"))
        self.assertTrue(re.match(pattern, "fileZ.txt"))
        self.assertTrue(re.match(pattern, "file5.txt"))
        self.assertFalse(re.match(pattern, "file-.txt"))

    def test_backslash_in_character_class(self):
        """[\\\\] matches literal backslash"""
        pattern = k3fnmatch.translate(r"file[\\].txt")
        self.assertTrue(re.match(pattern, r"file\.txt"))

    def test_negated_range(self):
        """[!a-z] matches any char except lowercase letters"""
        pattern = k3fnmatch.translate("file[!a-z].txt")
        self.assertTrue(re.match(pattern, "fileA.txt"))
        self.assertTrue(re.match(pattern, "file1.txt"))
        self.assertFalse(re.match(pattern, "filea.txt"))

    def test_invalid_reversed_range(self):
        """Test reversed ranges like [z-a] where end < start"""
        pattern = k3fnmatch.translate("file[z-a].txt")
        # Invalid range should be removed/empty
        self.assertFalse(re.match(pattern, "filez.txt"))
        self.assertFalse(re.match(pattern, "filea.txt"))

    def test_mixed_valid_invalid_ranges(self):
        """Test pattern with both valid and invalid ranges"""
        pattern = k3fnmatch.translate("file[a-z9-0].txt")
        # Valid range [a-z] should work
        self.assertTrue(re.match(pattern, "filea.txt"))
        self.assertTrue(re.match(pattern, "filez.txt"))
        # Invalid range [9-0] should be removed
        self.assertFalse(re.match(pattern, "file5.txt"))
        self.assertFalse(re.match(pattern, "file0.txt"))

    def test_overlapping_ranges(self):
        """Test overlapping character ranges"""
        # [a-mh-s] has ranges that overlap: a-m and h-s overlap at h-m
        pattern = k3fnmatch.translate("file[a-mh-s].txt")
        # Within first range [a-m]
        self.assertTrue(re.match(pattern, "filea.txt"))
        self.assertTrue(re.match(pattern, "filem.txt"))
        # Within second range [h-s]
        self.assertTrue(re.match(pattern, "fileh.txt"))
        self.assertTrue(re.match(pattern, "files.txt"))
        # In overlap region
        self.assertTrue(re.match(pattern, "filek.txt"))
        # Outside both ranges should fail
        self.assertFalse(re.match(pattern, "filet.txt"))
        self.assertFalse(re.match(pattern, "filez.txt"))


class TestCharacterClassSpecialCases(unittest.TestCase):
    """Test character class special cases for uncovered lines"""

    def test_empty_class_after_range_processing(self):
        """Test pattern where all ranges are invalid and removed"""
        # All invalid ranges should result in empty class
        pattern = k3fnmatch.translate("file[z-a9-0Z-A].txt")
        # Empty class matches nothing
        self.assertFalse(re.match(pattern, "filea.txt"))
        self.assertFalse(re.match(pattern, "file1.txt"))
        self.assertFalse(re.match(pattern, "fileZ.txt"))

    def test_character_class_starting_with_bracket(self):
        """Test class with literal [ at start"""
        # Pattern: file[[abc].txt matches [, a, b, or c
        pattern = k3fnmatch.translate("file[[abc].txt")
        self.assertTrue(re.match(pattern, "file[.txt"))
        self.assertTrue(re.match(pattern, "filea.txt"))
        self.assertTrue(re.match(pattern, "fileb.txt"))

    def test_truly_trailing_backslash(self):
        """Pattern ending with single backslash character"""
        # Create pattern with terminal backslash
        pattern = k3fnmatch.translate("file" + chr(92))
        self.assertTrue(re.match(pattern, "file\\"))
        self.assertFalse(re.match(pattern, "file"))


if __name__ == "__main__":
    unittest.main()
