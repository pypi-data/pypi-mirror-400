from tests.conftest import convert


class TestOrderedListLoose:
    """Test ordered_list_loose configuration."""

    def test_ordered_list_loose_enabled_default(self, md):
        """Test that blank lines create loose lists with <p> tags by default."""
        input = \
"""1. one

2. two

3. three"""
        expected = \
"""<ol>
<li>
<p>one</p>
</li>
<li>
<p>two</p>
</li>
<li>
<p>three</p>
</li>
</ol>"""
        result = convert(md, input)
        assert result == expected

    def test_ordered_list_loose_disabled(self, md_custom):
        """Test that disabling ordered_list_loose prevents <p> tag wrapping."""
        md = md_custom(ordered_list_loose=False)
        input = \
"""1. one

2. two

3. three"""
        expected = \
"""<ol>
<li>one</li>
<li>two</li>
<li>three</li>
</ol>"""
        result = convert(md, input)
        assert result == expected

    def test_ordered_list_loose_tight_list(self, md):
        """Test that tight lists (no blank lines) don't get <p> tags."""
        input = \
"""1. one
2. two
3. three"""
        expected = \
"""<ol>
<li>one</li>
<li>two</li>
<li>three</li>
</ol>"""
        result = convert(md, input)
        assert result == expected

    def test_ordered_list_loose_with_paragraphs(self, md):
        """Test loose lists with multiple paragraphs."""
        input = \
"""1. First item

  First paragraph in first item.

  Second paragraph in first item.

2. Second item

  Paragraph in second item."""
        expected = \
"""<ol>
<li>
<p>First item</p>
<p>First paragraph in first item.</p>
<p>Second paragraph in first item.</p>
</li>
<li>
<p>Second item</p>
<p>Paragraph in second item.</p>
</li>
</ol>"""
        result = convert(md, input)
        assert result == expected

    def test_ordered_list_loose_with_nested(self, md):
        """Test loose ordered lists with nested lists."""
        input = \
"""1. First item

  - Nested unordered
  - Another nested

2. Second item"""
        expected = \
"""<ol>
<li>
<p>First item</p>
<ul>
<li>Nested unordered</li>
<li>Another nested</li>
</ul>
</li>
<li>
<p>Second item</p>
</li>
</ol>"""
        result = convert(md, input)
        assert result == expected

    def test_ordered_list_loose_starting_not_at_one(self, md):
        """Test loose lists starting at numbers other than 1."""
        input = \
"""5. Fifth

6. Sixth

7. Seventh"""
        expected = \
"""<ol start="5">
<li>
<p>Fifth</p>
</li>
<li>
<p>Sixth</p>
</li>
<li>
<p>Seventh</p>
</li>
</ol>"""
        result = convert(md, input)
        assert result == expected

    def test_ordered_list_loose_with_preserve_numbers(self, md_custom):
        """Test loose lists with preserve_numbers enabled."""
        md = md_custom(ordered_list_loose=True, preserve_numbers=True)
        input = \
"""1. First

2. Second

2. Another second"""
        expected = \
"""<ol>
<li value="1">
<p>First</p>
</li>
<li value="2">
<p>Second</p>
</li>
<li value="2">
<p>Another second</p>
</li>
</ol>"""
        result = convert(md, input)
        assert result == expected

    def test_ordered_list_loose_disabled_with_preserve_numbers(self, md_custom):
        """Test tight lists with preserve_numbers enabled."""
        md = md_custom(ordered_list_loose=False, preserve_numbers=True)
        input = \
"""1. First

2. Second

2. Another second"""
        expected = \
"""<ol>
<li value="1">First</li>
<li value="2">Second</li>
<li value="2">Another second</li>
</ol>"""
        result = convert(md, input)
        assert result == expected

    def test_ordered_list_loose_with_code_block(self, md):
        """Test loose list with code block."""
        input = \
"""1. Item with code

      code block
      more code

2. Next item"""
        expected = \
"""<ol>
<li>
<p>Item with code</p>
<pre><code>code block
more code
</code></pre>
</li>
<li>
<p>Next item</p>
</li>
</ol>"""
        result = convert(md, input)
        assert result == expected

    def test_ordered_list_loose_mixed_spacing(self, md):
        """Test list with mixed spacing (some blank lines, some not)."""
        input = \
"""1. First

2. Second
3. Third

4. Fourth"""
        expected = \
"""<ol>
<li>
<p>First</p>
</li>
<li>
<p>Second</p>
</li>
<li>
<p>Third</p>
</li>
<li>
<p>Fourth</p>
</li>
</ol>"""
        result = convert(md, input)
        assert result == expected
