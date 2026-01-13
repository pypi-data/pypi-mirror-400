"""Basic tests for mdx_better_lists extension.

Write your TDD tests here! These examples show the testing pattern.
"""

from tests.conftest import convert


class TestSimpleUnorderedLists:
    """Test simple unordered lists."""

    def test_simple_minus_unordered_list(self, md):
        input = \
"""- Item A
- Item B
- Item C"""
        expected = \
"""<ul>
<li>Item A</li>
<li>Item B</li>
<li>Item C</li>
</ul>"""
        result = convert(md, input)
        assert result == expected

    def test_simple_plus_unordered_list(self, md):
        input = \
"""+ Item 1
+ Item 2
+ Item 3"""
        expected = \
"""<ul>
<li>Item 1</li>
<li>Item 2</li>
<li>Item 3</li>
</ul>"""
        result = convert(md, input)
        assert result == expected

    def test_simple_asterisk_unordered_list(self, md):
        input = \
"""* Alpha
* Beta
* Gamma"""
        expected = \
"""<ul>
<li>Alpha</li>
<li>Beta</li>
<li>Gamma</li>
</ul>"""
        result = convert(md, input)
        assert result == expected


class TestSimpleOrderedLists:
    """Test simple ordered lists."""
    def test_simple_numeric_ordered_list(self, md):
        input = \
"""1. First
2. Second
3. Third"""
        expected = \
"""<ol>
<li>First</li>
<li>Second</li>
<li>Third</li>
</ol>"""
        result = convert(md, input)
        assert result == expected
