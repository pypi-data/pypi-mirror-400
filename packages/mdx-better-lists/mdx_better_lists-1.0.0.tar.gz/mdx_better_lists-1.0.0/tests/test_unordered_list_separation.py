from tests.conftest import convert


class TestUnorderedListSeparation:
    """Test unordered_list_separation configuration."""

    def test_unordered_list_separation_enabled_default(self, md):
        """Test that blank lines separate unordered lists by default."""
        input = \
"""- First

- Second
- Third"""
        expected = \
"""<ul>
<li>First</li>
</ul>
<ul>
<li>Second</li>
<li>Third</li>
</ul>"""
        result = convert(md, input)
        assert result == expected

    def test_unordered_list_separation_disabled(self, md_custom):
        """Test that disabling unordered_list_separation keeps lists together."""
        md = md_custom(unordered_list_separation=False)
        input = \
"""- First

- Second
- Third"""
        expected = \
"""<ul>
<li>First</li>
<li>Second</li>
<li>Third</li>
</ul>"""
        result = convert(md, input)
        assert result == expected

    def test_unordered_list_separation_tight_list(self, md):
        """Test that tight lists stay together."""
        input = \
"""- First
- Second
- Third"""
        expected = \
"""<ul>
<li>First</li>
<li>Second</li>
<li>Third</li>
</ul>"""
        result = convert(md, input)
        assert result == expected

    def test_unordered_list_separation_multiple_blanks(self, md):
        """Test separation with multiple blank lines."""
        input = \
"""- First


- Second


- Third"""
        expected = \
"""<ul>
<li>First</li>
</ul>
<ul>
<li>Second</li>
</ul>
<ul>
<li>Third</li>
</ul>"""
        result = convert(md, input)
        assert result == expected

    def test_unordered_list_separation_with_paragraphs(self, md):
        """Test list separation with paragraphs in items."""
        input = \
"""- First item

  Paragraph in first.

- Second item

  Paragraph in second."""
        expected = \
"""<ul>
<li>
<p>First item</p>
<p>Paragraph in first.</p>
</li>
</ul>
<ul>
<li>
<p>Second item</p>
<p>Paragraph in second.</p>
</li>
</ul>"""
        result = convert(md, input)
        assert result == expected

    def test_unordered_list_separation_disabled_with_paragraphs(self, md_custom):
        """Test that disabled separation keeps lists with paragraphs together."""
        md = md_custom(unordered_list_separation=False)
        input = \
"""- First item

  Paragraph in first.

- Second item

  Paragraph in second."""
        expected = \
"""<ul>
<li>
<p>First item</p>
<p>Paragraph in first.</p>
</li>
<li>
<p>Second item</p>
<p>Paragraph in second.</p>
</li>
</ul>"""
        result = convert(md, input)
        assert result == expected

    def test_unordered_list_separation_with_nested(self, md):
        """Test separation with nested lists."""
        input = \
"""- Outer one
  - Nested
  - Another nested

- Outer two"""
        expected = \
"""<ul>
<li>Outer one<ul>
<li>Nested</li>
<li>Another nested</li>
</ul>
</li>
</ul>
<ul>
<li>Outer two</li>
</ul>"""
        result = convert(md, input)
        assert result == expected

    def test_unordered_list_separation_with_code(self, md):
        """Test separation with code blocks."""
        input = \
"""- Item with code

      code here

- Next item"""
        expected = \
"""<ul>
<li>Item with code<pre><code>code here
</code></pre>
</li>
</ul>
<ul>
<li>Next item</li>
</ul>"""
        result = convert(md, input)
        assert result == expected
