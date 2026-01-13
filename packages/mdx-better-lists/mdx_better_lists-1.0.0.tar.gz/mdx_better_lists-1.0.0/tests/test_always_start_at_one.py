from tests.conftest import convert


class TestAlwaysStartAtOne:
    """Test always_start_at_one configuration for ordered lists."""

    def test_always_start_at_one_disabled_default(self, md):
        """Test that default behavior preserves start attribute for non-1 starts."""
        input = \
"""5. Fifth item
6. Sixth item
7. Seventh item"""
        expected = \
"""<ol start="5">
<li>Fifth item</li>
<li>Sixth item</li>
<li>Seventh item</li>
</ol>"""
        result = convert(md, input)
        assert result == expected

    def test_always_start_at_one_enabled(self, md_custom):
        """Test that always_start_at_one forces lists to start at 1."""
        md = md_custom(always_start_at_one=True)
        input = \
"""5. Fifth item
6. Sixth item
7. Seventh item"""
        expected = \
"""<ol>
<li>Fifth item</li>
<li>Sixth item</li>
<li>Seventh item</li>
</ol>"""
        result = convert(md, input)
        assert result == expected

    def test_always_start_at_one_with_nested_lists(self, md_custom):
        """Test always_start_at_one with nested ordered lists."""
        md = md_custom(always_start_at_one=True)
        input = \
"""3. Third item
  5. Nested fifth
  6. Nested sixth
4. Fourth item"""
        expected = \
"""<ol>
<li>Third item<ol>
<li>Nested fifth</li>
<li>Nested sixth</li>
</ol>
</li>
<li>Fourth item</li>
</ol>"""
        result = convert(md, input)
        assert result == expected

    def test_always_start_at_one_off_with_nested_lists(self, md):
        """Test always_start_at_one with nested ordered lists."""
        input = \
"""3. Third item
  5. Nested fifth
  6. Nested sixth
4. Fourth item"""
        expected = \
"""<ol start="3">
<li>Third item<ol start="5">
<li>Nested fifth</li>
<li>Nested sixth</li>
</ol>
</li>
<li>Fourth item</li>
</ol>"""
        result = convert(md, input)
        assert result == expected
