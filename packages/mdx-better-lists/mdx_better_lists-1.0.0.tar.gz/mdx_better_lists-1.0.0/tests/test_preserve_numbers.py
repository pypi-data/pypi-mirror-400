from tests.conftest import convert


class TestPreserveNumbers:
    """Test preserve_numbers configuration for ordered lists."""

    def test_preserve_numbers_disabled(self, md):
        """Test that default behavior doesn't preserve numbers."""
        input = \
"""1. First
2. Second
2. Another second
2. Yet another second
3. Third"""
        expected = \
"""<ol>
<li>First</li>
<li>Second</li>
<li>Another second</li>
<li>Yet another second</li>
<li>Third</li>
</ol>"""
        result = convert(md, input)
        assert result == expected

    def test_preserve_numbers_enabled(self, md_custom):
        """Test that preserve_numbers config preserves exact numbers."""
        md = md_custom(preserve_numbers=True)
        input = \
"""1. First
2. Second
2. Another second
2. Yet another second
3. Third
3. Another third"""
        expected = \
"""<ol>
<li value="1">First</li>
<li value="2">Second</li>
<li value="2">Another second</li>
<li value="2">Yet another second</li>
<li value="3">Third</li>
<li value="3">Another third</li>
</ol>"""
        result = convert(md, input)
        assert result == expected

    def test_preserve_numbers_non_sequential(self, md_custom):
        """Test preserve_numbers with non-sequential numbers."""
        md = md_custom(preserve_numbers=True)
        input = \
"""1. First
5. Fifth
5. Another fifth
10. Tenth"""
        expected = \
"""<ol>
<li value="1">First</li>
<li value="5">Fifth</li>
<li value="5">Another fifth</li>
<li value="10">Tenth</li>
</ol>"""
        result = convert(md, input)
        assert result == expected

    def test_preserve_numbers_starting_not_at_one(self, md_custom):
        """Test preserve_numbers with list starting at non-1."""
        md = md_custom(preserve_numbers=True)
        input = \
"""7. Seventh
7. Another seventh
8. Eighth"""
        expected = \
"""<ol start="7">
<li value="7">Seventh</li>
<li value="7">Another seventh</li>
<li value="8">Eighth</li>
</ol>"""
        result = convert(md, input)
        assert result == expected

    def test_preserve_numbers_complex(self, md_custom):
        """Test preserve_numbers with complex list."""
        md = md_custom(preserve_numbers=True)
        input = \
"""3. Item three

  First paragraph in item three.

  Second paragraph in item three.

4. Item four in a new list
  Paragraph in item four
  that spans multiple
  lines.

  And another paragraph with a list:
  - Subitem one
  - Subitem two
    * Sub-subitem
      1. Deep item one
      1. Deep item one again
      2. Deep item two
  - Subitem three
5. Item five

1. And a new list
2. Continuing the new list
2. Another two
3. Ending the new list"""
        expected = \
"""<ol start="3">
<li value="3">
<p>Item three</p>
<p>First paragraph in item three.</p>
<p>Second paragraph in item three.</p>
</li>
<li value="4">
<p>Item four in a new list
  Paragraph in item four
  that spans multiple
  lines.</p>
<p>And another paragraph with a list:</p>
<ul>
<li>Subitem one</li>
<li>Subitem two<ul>
<li>Sub-subitem<ol>
<li value="1">Deep item one</li>
<li value="1">Deep item one again</li>
<li value="2">Deep item two</li>
</ol>
</li>
</ul>
</li>
<li>Subitem three</li>
</ul>
</li>
<li value="5">
<p>Item five</p>
</li>
<li value="1">
<p>And a new list</p>
</li>
<li value="2">Continuing the new list</li>
<li value="2">Another two</li>
<li value="3">Ending the new list</li>
</ol>"""
        result = convert(md, input)
        assert result == expected
