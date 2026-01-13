from tests.conftest import convert


class TestAdvanced:
    """Test advanced and complex list structures."""

    def test_ordered_list_starting_not_at_one(self, md):
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

    def test_ordered_list_non_sequential_numbers(self, md):
        input = \
"""1. First
3. Third
7. Seventh"""
        expected = \
"""<ol>
<li>First</li>
<li>Third</li>
<li>Seventh</li>
</ol>"""
        result = convert(md, input)
        assert result == expected

    def test_single_item_list(self, md):
        input = "- Only one item"
        expected = \
"""<ul>
<li>Only one item</li>
</ul>"""
        result = convert(md, input)
        assert result == expected

    def test_list_item_with_trailing_spaces(self, md):
        input = \
"""- Item with spaces
- Normal item
- More spaces     """
        expected = \
"""<ul>
<li>Item with spaces</li>
<li>Normal item</li>
<li>More spaces     </li>
</ul>"""
        result = convert(md, input)
        assert result == expected

    def test_very_long_list_item(self, md):
        input = "- This is a very long list item that contains a lot of text and should still be processed correctly without any issues even though it spans many characters and words and sentences."  # noqa: E501
        expected = \
"""<ul>
<li>This is a very long list item that contains a lot of text and should still be processed correctly without any issues even though it spans many characters and words and sentences.</li>
</ul>"""  # noqa: E501
        result = convert(md, input)
        assert result == expected

    def test_list_with_code_block(self, md):
        input = \
"""- Item with code:

      def hello():
          print("world")

- Next item"""
        expected = \
"""<ul>
<li>Item with code:<pre><code>def hello():
    print("world")
</code></pre>
</li>
</ul>
<ul>
<li>Next item</li>
</ul>"""
        result = convert(md, input)
        assert result == expected

    def test_list_with_blockquote(self, md):
        input = \
"""1. First item
2. Item with quote:
  > This is a quote
3. Third item"""
        expected = \
"""<ol>
<li>First item</li>
<li>Item with quote:<blockquote>
<p>This is a quote</p>
</blockquote>
</li>
<li>Third item</li>
</ol>"""
        result = convert(md, input)
        assert result == expected

    def test_complex_nested_with_separation(self, md):
        """Test preserve_numbers with complex nested lists and separation."""
        input = \
"""- First list item
  Paragraph in first item.

  - Subitem one
    - Sub-subitem one
    - Sub-subitem two
  - Subitem two
- Second list item

  This is a paragraph.

- New list item
  This item is of a new list.
1. First ordered item
   With paragraph in first ordered item.

   1. Nested ordered one
   2. Nested ordered two
     1. Deep nested one
       With a paragraph.

       And another paragraph with a list:
       1. Deep deep one
       2. Deep deep two
    3. Nested ordered three
2. Second ordered item"""
        expected = \
"""<ul>
<li>
<p>First list item
  Paragraph in first item.</p>
<ul>
<li>Subitem one<ul>
<li>Sub-subitem one</li>
<li>Sub-subitem two</li>
</ul>
</li>
<li>Subitem two</li>
</ul>
</li>
</ul>
<ul>
<li>
<p>Second list item</p>
<p>This is a paragraph.</p>
</li>
</ul>
<ul>
<li>
<p>New list item
  This item is of a new list.
1. First ordered item
   With paragraph in first ordered item.</p>
<ol>
<li>Nested ordered one</li>
<li>Nested ordered two<ol>
<li>
<p>Deep nested one
   With a paragraph.</p>
<p>And another paragraph with a list:</p>
<ol>
<li>Deep deep one</li>
<li>Deep deep two
    3. Nested ordered three</li>
</ol>
</li>
</ol>
</li>
</ol>
</li>
</ul>
<ol start="2">
<li>Second ordered item</li>
</ol>"""
        result = convert(md, input)
        assert result == expected
