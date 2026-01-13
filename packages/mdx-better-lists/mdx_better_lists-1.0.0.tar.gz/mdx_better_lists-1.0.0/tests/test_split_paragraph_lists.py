"""Tests for the split_paragraph_lists configuration option."""

from tests.conftest import convert


class TestSplitParagraphLists:
    """Test split_paragraph_lists configuration."""

    def test_split_paragraph_lists_disabled_default(self, md):
        """Test that split_paragraph_lists is disabled by default."""
        input = \
"""This is a paragraph before the list.
- First item
- Second item"""
        expected = \
"""<p>This is a paragraph before the list.
- First item
- Second item</p>"""
        result = convert(md, input)
        assert result == expected

    def test_split_paragraph_lists_enabled(self, md_custom):
        """Test split_paragraph_lists when enabled."""
        md = md_custom(split_paragraph_lists=True)
        input = \
"""This is a paragraph before the list.
- First item
- Second item"""
        expected = \
"""<p>This is a paragraph before the list.</p>
<ul>
<li>First item</li>
<li>Second item</li>
</ul>"""
        result = convert(md, input)
        assert result == expected

    def test_split_paragraph_lists_ordered_list(self, md_custom):
        """Test split_paragraph_lists with ordered lists."""
        md = md_custom(split_paragraph_lists=True)
        input = \
"""This is a paragraph before the list.
1. First item
2. Second item"""
        expected = \
"""<p>This is a paragraph before the list.</p>
<ol>
<li>First item</li>
<li>Second item</li>
</ol>"""
        result = convert(md, input)
        assert result == expected

    def test_split_paragraph_lists_disabled(self, md_custom):
        """Test split_paragraph_lists when disabled."""
        md = md_custom(split_paragraph_lists=False)
        input = \
"""This is a paragraph before the list.
- First item
- Second item"""
        expected = \
"""<p>This is a paragraph before the list.
- First item
- Second item</p>"""
        result = convert(md, input)
        assert result == expected

    def test_split_paragraph_lists_disabled_ordered(self, md_custom):
        """Test split_paragraph_lists disabled with ordered lists."""
        md = md_custom(split_paragraph_lists=False)
        input = \
"""This is a paragraph before the list.
1. First item
2. Second item"""
        expected = \
"""<p>This is a paragraph before the list.
1. First item
2. Second item</p>"""
        result = convert(md, input)
        assert result == expected

    def test_split_paragraph_lists_multiple_paragraphs(self, md_custom):
        """Test split_paragraph_lists with multiple paragraphs and lists."""
        md = md_custom(split_paragraph_lists=True)
        input = \
"""First paragraph.
- First list item
- Second list item

Another paragraph.
1. First ordered item
2. Second ordered item"""
        expected = \
"""<p>First paragraph.</p>
<ul>
<li>First list item</li>
<li>Second list item</li>
</ul>
<p>Another paragraph.</p>
<ol>
<li>First ordered item</li>
<li>Second ordered item</li>
</ol>"""
        result = convert(md, input)
        assert result == expected

    def test_split_paragraph_lists_with_blank_line(self, md_custom):
        """Test that blank lines still work as expected."""
        md = md_custom(split_paragraph_lists=True)
        input = \
"""This is a paragraph before the list.

- First item
- Second item"""
        expected = \
"""<p>This is a paragraph before the list.</p>
<ul>
<li>First item</li>
<li>Second item</li>
</ul>"""
        result = convert(md, input)
        assert result == expected

    def test_split_paragraph_lists_nested_context(self, md_custom):
        """Test that properly indented list markers become nested lists."""
        md = md_custom(split_paragraph_lists=True)
        input = \
"""- First item
  This is a paragraph
  1. This becomes a nested list
- Second item"""
        expected = \
"""<ul>
<li>First item
  This is a paragraph<ol>
<li>This becomes a nested list</li>
</ol>
</li>
<li>Second item</li>
</ul>"""
        result = convert(md, input)
        assert result == expected

    def test_split_paragraph_lists_different_markers(self, md_custom):
        """Test split_paragraph_lists with different list markers."""
        md = md_custom(split_paragraph_lists=True)
        input = \
"""Paragraph before plus marker.
+ First item
+ Second item
* First item
- First item"""
        expected = \
"""<p>Paragraph before plus marker.</p>
<ul>
<li>First item</li>
<li>Second item</li>
</ul>
<ul>
<li>First item</li>
</ul>
<ul>
<li>First item</li>
</ul>"""
        result = convert(md, input)
        assert result == expected

    def test_split_paragraph_lists_multiline_paragraph(self, md_custom):
        """Test split with multiline paragraph before list."""
        md = md_custom(split_paragraph_lists=True)
        input = \
"""This is a longer paragraph
that spans multiple lines
before the list starts.
- First item
- Second item"""
        expected = \
"""<p>This is a longer paragraph
that spans multiple lines
before the list starts.</p>
<ul>
<li>First item</li>
<li>Second item</li>
</ul>"""
        result = convert(md, input)
        assert result == expected

    def test_split_paragraph_lists_ordered_starting_not_at_one(self, md_custom):
        """Test split with ordered list not starting at 1."""
        md = md_custom(split_paragraph_lists=True)
        input = \
"""This is a paragraph.
3. Third item
4. Fourth item"""
        expected = \
"""<p>This is a paragraph.</p>
<ol start="3">
<li>Third item</li>
<li>Fourth item</li>
</ol>"""
        result = convert(md, input)
        assert result == expected
