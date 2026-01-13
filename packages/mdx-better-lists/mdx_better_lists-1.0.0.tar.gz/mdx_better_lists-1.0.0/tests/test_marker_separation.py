from tests.conftest import convert


class TestMarkerSeparation:
    """Test marker_separation configuration for unordered lists."""

    def test_marker_separation_enabled_default(self, md):
        """Test that default behavior separates different marker types."""
        input = \
"""- Dash item
+ Plus item
* Star item"""
        expected = \
"""<ul>
<li>Dash item</li>
</ul>
<ul>
<li>Plus item</li>
</ul>
<ul>
<li>Star item</li>
</ul>"""
        result = convert(md, input)
        assert result == expected

    def test_marker_separation_disabled(self, md_custom):
        """Test that disabling marker_separation allows mixed markers in same list."""
        md = md_custom(marker_separation=False)
        input = \
"""- Dash item
+ Plus item
* Star item"""
        expected = \
"""<ul>
<li>Dash item</li>
<li>Plus item</li>
<li>Star item</li>
</ul>"""
        result = convert(md, input)
        assert result == expected

    def test_marker_separation_same_marker_continues_list(self, md):
        """Test that same marker type continues the same list."""
        input = \
"""- First dash
- Second dash
- Third dash"""
        expected = \
"""<ul>
<li>First dash</li>
<li>Second dash</li>
<li>Third dash</li>
</ul>"""
        result = convert(md, input)
        assert result == expected

    def test_marker_separation_dash_to_plus(self, md):
        """Test separation when switching from dash to plus."""
        input = \
"""- Dash item one
- Dash item two
+ Plus item one
+ Plus item two"""
        expected = \
"""<ul>
<li>Dash item one</li>
<li>Dash item two</li>
</ul>
<ul>
<li>Plus item one</li>
<li>Plus item two</li>
</ul>"""
        result = convert(md, input)
        assert result == expected

    def test_marker_separation_dash_to_star(self, md):
        """Test separation when switching from dash to star."""
        input = \
"""- Dash item
* Star item"""
        expected = \
"""<ul>
<li>Dash item</li>
</ul>
<ul>
<li>Star item</li>
</ul>"""
        result = convert(md, input)
        assert result == expected

    def test_marker_separation_plus_to_star(self, md):
        """Test separation when switching from plus to star."""
        input = \
"""+ Plus item
* Star item"""
        expected = \
"""<ul>
<li>Plus item</li>
</ul>
<ul>
<li>Star item</li>
</ul>"""
        result = convert(md, input)
        assert result == expected

    def test_marker_separation_multiple_switches(self, md):
        """Test multiple marker switches."""
        input = \
"""- Dash
+ Plus
- Dash again
* Star
- Dash once more"""
        expected = \
"""<ul>
<li>Dash</li>
</ul>
<ul>
<li>Plus</li>
</ul>
<ul>
<li>Dash again</li>
</ul>
<ul>
<li>Star</li>
</ul>
<ul>
<li>Dash once more</li>
</ul>"""
        result = convert(md, input)
        assert result == expected

    def test_marker_separation_with_nested_lists(self, md):
        """Test marker separation with nested lists."""
        input = \
"""- Outer dash
  + Nested plus
  + Another nested plus
- Outer dash two
+ Outer plus"""
        expected = \
"""<ul>
<li>Outer dash<ul>
<li>Nested plus</li>
<li>Another nested plus</li>
</ul>
</li>
<li>Outer dash two</li>
</ul>
<ul>
<li>Outer plus</li>
</ul>"""
        result = convert(md, input)
        assert result == expected

    def test_marker_separation_disabled_with_nested(self, md_custom):
        """Test marker_separation=False with nested lists."""
        md = md_custom(marker_separation=False)
        input = \
"""- Outer dash
  + Nested plus
* Outer star"""
        expected = \
"""<ul>
<li>Outer dash<ul>
<li>Nested plus</li>
</ul>
</li>
<li>Outer star</li>
</ul>"""
        result = convert(md, input)
        assert result == expected

    def test_marker_separation_with_paragraphs(self, md):
        """Test marker separation with multi-paragraph items."""
        input = \
"""- Dash item

  Paragraph in dash item

+ Plus item

  Paragraph in plus item"""
        expected = \
"""<ul>
<li>
<p>Dash item</p>
<p>Paragraph in dash item</p>
</li>
</ul>
<ul>
<li>
<p>Plus item</p>
<p>Paragraph in plus item</p>
</li>
</ul>"""
        result = convert(md, input)
        assert result == expected

    def test_marker_separation_explicit_paragraph_break(self, md):
        """Test that explicit paragraph breaks still separate lists."""
        input = \
"""- Dash item

Text between lists

- Dash item again"""
        expected = \
"""<ul>
<li>Dash item</li>
</ul>
<p>Text between lists</p>
<ul>
<li>Dash item again</li>
</ul>"""
        result = convert(md, input)
        assert result == expected

    def test_marker_separation_complex_nested(self, md):
        """Test complex nested structure with marker separation."""
        input = \
"""- Outer dash one
  * Nested star
    + Deep nested plus
    + Deep nested plus two
  * Nested star two
- Outer dash two
+ Outer plus
  - Nested dash
* Outer star"""
        expected = \
"""<ul>
<li>Outer dash one<ul>
<li>Nested star<ul>
<li>Deep nested plus</li>
<li>Deep nested plus two</li>
</ul>
</li>
<li>Nested star two</li>
</ul>
</li>
<li>Outer dash two</li>
</ul>
<ul>
<li>Outer plus<ul>
<li>Nested dash</li>
</ul>
</li>
</ul>
<ul>
<li>Outer star</li>
</ul>"""
        result = convert(md, input)
        assert result == expected
