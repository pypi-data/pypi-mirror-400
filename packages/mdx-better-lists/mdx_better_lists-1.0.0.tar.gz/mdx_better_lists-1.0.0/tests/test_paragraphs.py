from tests.conftest import convert


class TestParagraphsInLists:
    """Test paragraph handling in lists."""

    def test_paragraph_item_lists(self, md):
        input = \
"""- Item 1
this is a paragraph in item 1.
- Item 2
this is a paragraph in item 2."""
        expected = \
"""<ul>
<li>Item 1
this is a paragraph in item 1.</li>
<li>Item 2
this is a paragraph in item 2.</li>
</ul>"""
        result = convert(md, input)
        assert result == expected

    def test_indented_paragraph_item_lists(self, md):
        input = \
"""1. Item 1
  this is a paragraph in item 1.
2. Item 2
  this is a paragraph in item 2."""
        expected = \
"""<ol>
<li>Item 1
  this is a paragraph in item 1.</li>
<li>Item 2
  this is a paragraph in item 2.</li>
</ol>"""
        result = convert(md, input)
        assert result == expected

    def test_weird_indented_paragraph_item_lists(self, md):
        input = \
"""* Item 1
 this is a paragraph in item 1.
* Item 2
    this is a paragraph in item 2.
* Item 3
     this is a paragraph in item 3."""
        expected = \
"""<ul>
<li>Item 1
 this is a paragraph in item 1.</li>
<li>Item 2
    this is a paragraph in item 2.</li>
<li>Item 3
     this is a paragraph in item 3.</li>
</ul>"""
        result = convert(md, input)
        assert result == expected

    def test_multi_line_paragraphs_in_list_items(self, md):
        input = \
"""1. Item 1
This is a paragraph in item 1
that continues here,
and even here.
2. Item 2
  This is a paragraph in item 2
  that also continues here."""
        expected = \
"""<ol>
<li>Item 1
This is a paragraph in item 1
that continues here,
and even here.</li>
<li>Item 2
  This is a paragraph in item 2
  that also continues here.</li>
</ol>"""
        result = convert(md, input)
        assert result == expected

    def test_multiple_paragraphs_in_list_items(self, md):
        input = \
"""- Item 1

  This is the first paragraph in item 1.

  This is the second paragraph in item 1.

- Item 2

  This is the first paragraph in item 2.

  This is the second paragraph in item 2.

  This is the third paragraph in item 2."""
        expected = \
"""<ul>
<li>
<p>Item 1</p>
<p>This is the first paragraph in item 1.</p>
<p>This is the second paragraph in item 1.</p>
</li>
</ul>
<ul>
<li>
<p>Item 2</p>
<p>This is the first paragraph in item 2.</p>
<p>This is the second paragraph in item 2.</p>
<p>This is the third paragraph in item 2.</p>
</li>
</ul>"""
        result = convert(md, input)
        assert result == expected

    def test_preserve_numbers_with_paragraphs(self, md_custom):
        """Test preserve_numbers with paragraphs in list items."""
        md = md_custom(preserve_numbers=True)
        input = \
"""1. First item
This is a paragraph in first item.
2. Second item
2. Another second item
This is a paragraph in another second item.
3. Third item"""
        expected = \
"""<ol>
<li value="1">First item
This is a paragraph in first item.</li>
<li value="2">Second item</li>
<li value="2">Another second item
This is a paragraph in another second item.</li>
<li value="3">Third item</li>
</ol>"""
        result = convert(md, input)
        assert result == expected

    def test_multiple_paragraphs_with_preserve_numbers(self, md_custom):
        """Test preserve_numbers with multiple paragraphs in list items."""
        md = md_custom(preserve_numbers=True)
        input = \
"""1. First item

  This is the first paragraph in first item.

  This is the second paragraph in first item.

2. Second item

  This is the first paragraph in second item.

2. Another second item

  This is the first paragraph in another second item.

  This is the second paragraph in another second item.

3. Third item"""
        expected = \
"""<ol>
<li value="1">
<p>First item</p>
<p>This is the first paragraph in first item.</p>
<p>This is the second paragraph in first item.</p>
</li>
<li value="2">
<p>Second item</p>
<p>This is the first paragraph in second item.</p>
</li>
<li value="2">
<p>Another second item</p>
<p>This is the first paragraph in another second item.</p>
<p>This is the second paragraph in another second item.</p>
</li>
<li value="3">
<p>Third item</p>
</li>
</ol>"""
        result = convert(md, input)
        assert result == expected
