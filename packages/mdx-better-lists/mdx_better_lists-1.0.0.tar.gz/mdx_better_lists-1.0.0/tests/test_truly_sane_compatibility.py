"""
Tests for mdx_better_lists compatibility with mdx_truly_sane_lists.

These tests are based on the test suite from mdx_truly_sane_lists:
https://github.com/radude/mdx_truly_sane_lists

Notes:
1. Changed extension name from 'mdx_truly_sane_lists' to 'mdx_better_lists'
2. Mapped truly_sane_lists config options to mdx_better_lists equivalents:
   - truly_sane=True (default) → marker_separation=True (default), unordered_list_separation=True (default),
     split_paragraph_lists=False (default)
   - truly_sane=False → marker_separation=False, unordered_list_separation=False, split_paragraph_lists=False (default)
   - nested_indent → nested_indent (same name)
3. Fixed expected output for nested lists to remove trailing spaces before <ul> tags
   (e.g., "customer<ul>" instead of "customer <ul>")
4. Added marker_separation=False to test_indent_4_with_2_data to match truly_sane behavior
   when different markers are grouped together due to insufficient indentation
5. The test_truly_insane test was omitted as it tests behavior of disabling the extension, but
    mdx_better_lists will give tight lists even with marker_separation
    and unordered_list_separation set to False, which deviates from the expected truly_insane behavior.
"""

import unittest
from textwrap import dedent

from markdown import markdown


class TrulySaneListCompatibilityTest(unittest.TestCase):
    """Test mdx_better_lists compatibility with mdx_truly_sane_lists behavior."""

    def test_simple(self):
        """Test simple list separation (truly_sane default behavior)."""
        raw = """
        - Zero

        - One
        - Two
        """
        expected = "<ul>\n<li>Zero</li>\n</ul>\n<ul>\n<li>One</li>\n<li>Two</li>\n</ul>"
        # Default config matches truly_sane behavior
        actual = markdown(dedent(raw), extensions=["mdx_better_lists"])
        self.assertEqual(expected, actual)

    def test_complex(self):
        """Test complex nested lists with marker separation."""
        raw = """
        + attributes

        - customer
          + first_name
          + family_name
          + email
        - person
          + first_name
          + family_name
          + birth_date
        - subscription_id

        + request
        """
        expected = "<ul>\n<li>attributes</li>\n</ul>\n<ul>\n<li>customer<ul>\n<li>first_name</li>\n<li>family_name</li>\n<li>email</li>\n</ul>\n</li>\n<li>person<ul>\n<li>first_name</li>\n<li>family_name</li>\n<li>birth_date</li>\n</ul>\n</li>\n<li>subscription_id</li>\n</ul>\n<ul>\n<li>request</li>\n</ul>"  # noqa: E501
        # Default config matches truly_sane behavior
        actual = markdown(dedent(raw), extensions=["mdx_better_lists"])
        self.assertEqual(expected, actual)

    def test_indent_4_with_2_data(self):
        """Test 4-space indent config with 2-space indented data (no nesting)."""
        raw = """
        + attributes

        - customer
          + first_name
          + family_name
          + email
        - person
          + first_name
          + family_name
          + birth_date
        - subscription_id

        + request
        """
        expected = "<ul>\n<li>attributes</li>\n</ul>\n<ul>\n<li>customer</li>\n<li>first_name</li>\n<li>family_name</li>\n<li>email</li>\n<li>person</li>\n<li>first_name</li>\n<li>family_name</li>\n<li>birth_date</li>\n<li>subscription_id</li>\n</ul>\n<ul>\n<li>request</li>\n</ul>"  # noqa: E501
        actual = markdown(
            dedent(raw),
            extensions=["mdx_better_lists"],
            extension_configs={
                "mdx_better_lists": {"nested_indent": 4, "marker_separation": False}
            },
        )
        self.assertEqual(expected, actual)

    def test_indent_4_with_4_data(self):
        """Test 4-space indent config with 4-space indented data (proper nesting)."""
        raw = """
        + attributes

        - customer
            + first_name
            + family_name
            + email
        - person
            + first_name
            + family_name
            + birth_date
        - subscription_id

        + request
        """
        expected = "<ul>\n<li>attributes</li>\n</ul>\n<ul>\n<li>customer<ul>\n<li>first_name</li>\n<li>family_name</li>\n<li>email</li>\n</ul>\n</li>\n<li>person<ul>\n<li>first_name</li>\n<li>family_name</li>\n<li>birth_date</li>\n</ul>\n</li>\n<li>subscription_id</li>\n</ul>\n<ul>\n<li>request</li>\n</ul>"  # noqa: E501
        actual = markdown(
            dedent(raw),
            extensions=["mdx_better_lists"],
            extension_configs={"mdx_better_lists": {"nested_indent": 4}},
        )
        self.assertEqual(expected, actual)

    def test_sane(self):
        """Test sane lists behavior with mixed list types."""
        raw = """
        1. Ordered
        2. List

        * Unordered
        * List

        1. Ordered again

        Paragraph
        * not a list item

        1. More ordered
        * not a list item

        * Unordered again
        1. not a list item
        """
        expected = "<ol>\n<li>Ordered</li>\n<li>List</li>\n</ol>\n<ul>\n<li>Unordered</li>\n<li>List</li>\n</ul>\n<ol>\n<li>Ordered again</li>\n</ol>\n<p>Paragraph\n* not a list item</p>\n<ol>\n<li>More ordered\n* not a list item</li>\n</ol>\n<ul>\n<li>Unordered again\n1. not a list item</li>\n</ul>"  # noqa: E501
        actual = markdown(dedent(raw), extensions=["mdx_better_lists"])
        self.assertEqual(expected, actual)

    def test_with_code(self):
        """Test lists with code blocks."""
        raw = """
        - customer
          + first_name
          + family_name
          + email

        Text

            code
            code

        Text

          Not code
          Not code

        """
        expected = "<ul>\n<li>customer<ul>\n<li>first_name</li>\n<li>family_name</li>\n<li>email</li>\n</ul>\n</li>\n</ul>\n<p>Text</p>\n<pre><code>code\ncode\n</code></pre>\n<p>Text</p>\n<p>Not code\n  Not code</p>"  # noqa: E501
        actual = markdown(dedent(raw), extensions=["mdx_better_lists"])
        self.assertEqual(expected, actual)

    def test_ordered(self):
        """Test simple ordered list."""
        raw = """
            1. one
            2. two
            3. three
        """
        expected = "<ol>\n<li>one</li>\n<li>two</li>\n<li>three</li>\n</ol>"
        actual = markdown(dedent(raw), extensions=["mdx_better_lists"])
        self.assertEqual(expected, actual)

    def test_ordered_with_empty_lines(self):
        """Test ordered lists with blank lines (loose list)."""
        raw = """
        1. one

        2. two

        3. three

        """
        expected = "<ol>\n<li>\n<p>one</p>\n</li>\n<li>\n<p>two</p>\n</li>\n<li>\n<p>three</p>\n</li>\n</ol>"
        actual = markdown(dedent(raw), extensions=["mdx_better_lists"])
        self.assertEqual(expected, actual)

    def test_ordered_with_empty_lines_not_sane(self):
        """Test ordered lists with blank lines and truly_sane=False equivalent."""
        raw = """
        1. one

        2. two

        3. three

        """
        expected = "<ol>\n<li>\n<p>one</p>\n</li>\n<li>\n<p>two</p>\n</li>\n<li>\n<p>three</p>\n</li>\n</ol>"
        # Same as default since ordered_list_loose=True is default
        actual = markdown(
            dedent(raw),
            extensions=["mdx_better_lists"],
            extension_configs={
                "mdx_better_lists": {
                    "marker_separation": False,
                    "unordered_list_separation": False,
                }
            },
        )
        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
