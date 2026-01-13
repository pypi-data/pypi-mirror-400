from tests.conftest import convert


class TestListSeparation:
    """Test list separation behavior."""

    def test_blank_line_lists(self, md):
        text = \
"""- List 1 First
- List 1 Second

- List 1 Third
- List 1 Fourth"""
        expected = \
"""<ul>
<li>List 1 First</li>
<li>List 1 Second</li>
</ul>
<ul>
<li>List 1 Third</li>
<li>List 1 Fourth</li>
</ul>"""
        result = convert(md, text)
        assert result == expected

    def test_multiple_blank_lines_lists(self, md):
        text = \
"""1. List A First
2. List A Second



3. List A Third


4. List A Fourth"""
        expected = \
"""<ol>
<li>List A First</li>
<li>
<p>List A Second</p>
</li>
<li>
<p>List A Third</p>
</li>
<li>
<p>List A Fourth</p>
</li>
</ol>"""
        result = convert(md, text)
        assert result == expected

    def test_heading_separates_lists(self, md):
        text = \
"""* List X First
* List X Second
# Heading Between Lists
* List Y First
* List Y Second"""
        expected = \
"""<ul>
<li>List X First</li>
<li>List X Second</li>
</ul>
<h1>Heading Between Lists</h1>
<ul>
<li>List Y First</li>
<li>List Y Second</li>
</ul>"""
        result = convert(md, text)
        assert result == expected

    def test_list_then_paragraph_then_list(self, md):
        input = \
"""- List A first list item
- List A second list item

This is a paragraph between lists.

- List B first list item
- List B second list item"""
        expected = \
"""<ul>
<li>List A first list item</li>
<li>List A second list item</li>
</ul>
<p>This is a paragraph between lists.</p>
<ul>
<li>List B first list item</li>
<li>List B second list item</li>
</ul>"""
        result = convert(md, input)
        assert result == expected

    def test_paragraph_then_list(self, md):
        input = \
"""This is a paragraph before the list.

- List item 1
- List item 2"""
        expected = \
"""<p>This is a paragraph before the list.</p>
<ul>
<li>List item 1</li>
<li>List item 2</li>
</ul>"""
        result = convert(md, input)
        assert result == expected

    def test_list_then_paragraph(self, md):
        input = \
"""- List item 1
- List item 2

This is a paragraph after the list."""
        expected = \
"""<ul>
<li>List item 1</li>
<li>List item 2</li>
</ul>
<p>This is a paragraph after the list.</p>"""
        result = convert(md, input)
        assert result == expected

    def test_heading(self, md):
        input = \
"""# Heading

- List item 1
- List item 2

Regular paragraph.

1. Ordered item 1
2. Ordered item 2"""
        expected = \
"""<h1>Heading</h1>
<ul>
<li>List item 1</li>
<li>List item 2</li>
</ul>
<p>Regular paragraph.</p>
<ol>
<li>Ordered item 1</li>
<li>Ordered item 2</li>
</ol>"""
        result = convert(md, input)
        assert result == expected

    def test_preserve_numbers_with_separated_lists(self, md_custom):
        """Test preserve_numbers with separated lists."""
        md = md_custom(preserve_numbers=True)
        input = \
"""1. First list item
2. Second list item
2. Another second

This is a paragraph separating lists.

3. New list first item
3. New list second item
5. New list third item"""
        expected = \
"""<ol>
<li value="1">First list item</li>
<li value="2">Second list item</li>
<li value="2">Another second</li>
</ol>
<p>This is a paragraph separating lists.</p>
<ol start="3">
<li value="3">New list first item</li>
<li value="3">New list second item</li>
<li value="5">New list third item</li>
</ol>"""
        result = convert(md, input)
        assert result == expected
