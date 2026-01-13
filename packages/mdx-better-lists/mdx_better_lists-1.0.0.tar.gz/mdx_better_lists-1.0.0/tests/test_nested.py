from tests.conftest import convert


class TestNestedLists:
    """Test nested lists behavior."""

    def test_nested_list_with_2_space_indent(self, md):
        input = \
"""- Item 1
  - Nested 1
  - Nested 2
- Item 2"""
        expected = \
"""<ul>
<li>Item 1<ul>
<li>Nested 1</li>
<li>Nested 2</li>
</ul>
</li>
<li>Item 2</li>
</ul>"""
        result = convert(md, input)
        assert result == expected

    def test_nested_list_with_4_space_indent(self, md_custom):
        md = md_custom(nested_indent=4)
        input = \
"""- Item A
    - Nested A1
    - Nested A2
- Item B"""
        expected = \
"""<ul>
<li>Item A<ul>
<li>Nested A1</li>
<li>Nested A2</li>
</ul>
</li>
<li>Item B</li>
</ul>"""
        result = convert(md, input)
        assert result == expected

    def test_mixed_nested_lists(self, md):
        input = \
"""1. Item 1
  - Subitem 1
  - Subitem 2
2. Item 2
  1. Subitem 2.1
  2. Subitem 2.2"""
        expected = \
"""<ol>
<li>Item 1<ul>
<li>Subitem 1</li>
<li>Subitem 2</li>
</ul>
</li>
<li>Item 2<ol>
<li>Subitem 2.1</li>
<li>Subitem 2.2</li>
</ol>
</li>
</ol>"""
        result = convert(md, input)
        assert result == expected

    def test_deeply_nested_lists(self, md):
        input = \
"""- Level 1
  - Level 2
    - Level 3
      - Level 4
- Back to Level 1"""
        expected = \
"""<ul>
<li>Level 1<ul>
<li>Level 2<ul>
<li>Level 3<ul>
<li>Level 4</li>
</ul>
</li>
</ul>
</li>
</ul>
</li>
<li>Back to Level 1</li>
</ul>"""
        result = convert(md, input)
        assert result == expected

    def test_preserve_numbers_with_nested_lists(self, md_custom):
        """Test preserve_numbers with nested ordered lists."""
        md = md_custom(preserve_numbers=True)
        input = \
"""1. First
2. Second
2. Another second
  1. Nested first
  2. Nested second
  2. Nested repeat
3. Third"""
        expected = \
"""<ol>
<li value="1">First</li>
<li value="2">Second</li>
<li value="2">Another second<ol>
<li value="1">Nested first</li>
<li value="2">Nested second</li>
<li value="2">Nested repeat</li>
</ol>
</li>
<li value="3">Third</li>
</ol>"""
        result = convert(md, input)
        assert result == expected

    def test_preserve_numbers_with_mixed_nested_lists(self, md_custom):
        """Test preserve_numbers with mixed nested lists."""
        md = md_custom(preserve_numbers=True)
        input = \
"""1. Outer one
1. Outer one again
  - Unordered nested
  - Another unordered
2. Outer two
  3. Inner three
  3. Inner three again
  5. Inner five"""
        expected = \
"""<ol>
<li value="1">Outer one</li>
<li value="1">Outer one again<ul>
<li>Unordered nested</li>
<li>Another unordered</li>
</ul>
</li>
<li value="2">Outer two<ol start="3">
<li value="3">Inner three</li>
<li value="3">Inner three again</li>
<li value="5">Inner five</li>
</ol>
</li>
</ol>"""
        result = convert(md, input)
        assert result == expected

    def test_preserve_numbers_deeply_nested(self, md_custom):
        """Test preserve_numbers with deeply nested ordered lists."""
        md = md_custom(preserve_numbers=True)
        input = \
"""1. Level 1
1. Level 1 again
  2. Level 2
  2. Level 2 repeat
    5. Level 3
    5. Level 3 repeat
2. Back to Level 1"""
        expected = \
"""<ol>
<li value="1">Level 1</li>
<li value="1">Level 1 again<ol start="2">
<li value="2">Level 2</li>
<li value="2">Level 2 repeat<ol start="5">
<li value="5">Level 3</li>
<li value="5">Level 3 repeat</li>
</ol>
</li>
</ol>
</li>
<li value="2">Back to Level 1</li>
</ol>"""
        result = convert(md, input)
        assert result == expected
