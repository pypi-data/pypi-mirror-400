# mdx_better_lists

[![PyPI](https://img.shields.io/pypi/v/mdx-better-lists)](https://pypi.org/project/mdx-better-lists/)
[![Python Versions](https://img.shields.io/pypi/pyversions/mdx-better-lists)](https://pypi.org/project/mdx-better-lists/)
[![License](https://img.shields.io/pypi/l/mdx-better-lists)](https://github.com/JimmyOei/mdx_better_lists/blob/main/LICENSE)
[![CI](https://github.com/JimmyOei/mdx_better_lists/workflows/CI/badge.svg)](https://github.com/JimmyOei/mdx_better_lists/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/JimmyOei/mdx_better_lists/branch/main/graph/badge.svg)](https://codecov.io/gh/JimmyOei/mdx_better_lists)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Python-Markdown extension for better list handling, providing more intuitive list behavior and formatting with fine-grained control over list rendering. Created with Test-Driven Development (TDD) principles to ensure reliability and maintainability.

## Features

- **Configurable nested indentation** - Control how many spaces are required for nested lists (default: 2)
- **Marker-based list separation** - Automatically separate lists when marker types change (-, *, +)
- **Blank line list separation** - Separate unordered lists when blank lines appear between items
- **Loose list control** - Control paragraph wrapping in ordered lists with blank lines
- **Number preservation** - Optionally preserve exact list numbers from markdown source
- **Always start at one** - Force ordered lists to always start at 1
- **Paragraph-list splitting** - Optionally split paragraphs and lists without requiring blank lines between them

## Installation

```bash
pip install mdx_better_lists
```

## Usage

### Basic Usage

```python
from markdown import markdown

text = """
- Item 1
- Item 2

- Item 3
"""

html = markdown(text, extensions=['mdx_better_lists'])
```

### With Configuration

```python
from markdown import markdown

text = """
1. First
2. Second
2. Another second
"""

html = markdown(text, extensions=['mdx_better_lists'],
                extension_configs={'mdx_better_lists': {
                    'preserve_numbers': True
                }})
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `nested_indent` | int | 2 | Number of spaces required for nested list indentation |
| `marker_separation` | bool | True | Separate lists when marker types (-, *, +) differ |
| `unordered_list_separation` | bool | True | Separate unordered lists when blank lines appear between items |
| `ordered_list_loose` | bool | True | Wrap ordered list items in `<p>` tags when blank lines separate them |
| `preserve_numbers` | bool | False | Preserve exact list numbers from markdown (use `value` attribute) |
| `always_start_at_one` | bool | False | Force all ordered lists to start at 1 |
| `split_paragraph_lists` | bool | False | Split paragraphs and lists when they appear without blank lines between them |

### Configuration Details

#### `nested_indent` (default: 2)

Controls how many spaces are required for a list item to be considered nested.

```python
# With nested_indent=2 (default)
- Parent
  - Nested  # 2 spaces = nested

# With nested_indent=4
- Parent
    - Nested  # 4 spaces = nested
  - Not nested  # 2 spaces = not nested
```

#### `marker_separation` (default: True)

When enabled, lists with different markers (-, *, +) are separated into different `<ul>` elements.

```python
# With marker_separation=True (default)
- Item with dash
+ Item with plus  # Creates a new <ul>

# Output: Two separate <ul> elements

# With marker_separation=False
- Item with dash
+ Item with plus  # Same <ul>

# Output: Single <ul> element
```

#### `unordered_list_separation` (default: True)

When enabled, unordered lists are separated into different `<ul>` elements when blank lines appear.

```python
# With unordered_list_separation=True (default)
- First

- Second  # Creates a new <ul>

# Output: Two separate <ul> elements

# With unordered_list_separation=False
- First

- Second  # Same <ul>

# Output: Single <ul> element
```

#### `ordered_list_loose` (default: True)

When enabled, ordered list items are wrapped in `<p>` tags when blank lines separate them.

```python
# With ordered_list_loose=True (default)
1. First

2. Second

# Output:
<ol>
  <li><p>First</p></li>
  <li><p>Second</p></li>
</ol>

# With ordered_list_loose=False
1. First

2. Second

# Output:
<ol>
  <li>First</li>
  <li>Second</li>
</ol>
```

#### `preserve_numbers` (default: False)

When enabled, preserves exact list numbers from the markdown source using the `value` attribute.

```python
# With preserve_numbers=True
1. First
2. Second
2. Another second
3. Third

# Output:
<ol>
  <li value="1">First</li>
  <li value="2">Second</li>
  <li value="2">Another second</li>
  <li value="3">Third</li>
</ol>
```

#### `always_start_at_one` (default: False)

When enabled, forces all ordered lists to start at 1, ignoring the starting number in markdown.

```python
# With always_start_at_one=True
5. Fifth
6. Sixth

# Output:
<ol>
  <li>Fifth</li>
  <li>Sixth</li>
</ol>
# (renders as 1, 2 instead of 5, 6)

# With always_start_at_one=False (default)
5. Fifth
6. Sixth

# Output:
<ol start="5">
  <li>Fifth</li>
  <li>Sixth</li>
</ol>
```

#### `split_paragraph_lists` (default: False)

When enabled, automatically splits paragraphs and lists that appear without blank lines between them into separate blocks. This allows lists to be recognized immediately after paragraphs without requiring a blank line separator.

```python
# With split_paragraph_lists=False (default)
This is a paragraph before the list.
- First item
- Second item

# Output:
<p>This is a paragraph before the list.
- First item
- Second item</p>
# (list markers are treated as plain text)

# With split_paragraph_lists=True
This is a paragraph before the list.
- First item
- Second item

# Output:
<p>This is a paragraph before the list.</p>
<ul>
  <li>First item</li>
  <li>Second item</li>
</ul>
# (paragraph and list are separated)
```

This also works with ordered lists:

```python
# With split_paragraph_lists=True
Introduction paragraph.
1. First point
2. Second point

# Output:
<p>Introduction paragraph.</p>
<ol>
  <li>First point</li>
  <li>Second point</li>
</ol>
```

**Note:** This feature only operates at the top level. List markers inside list items that are not properly indented will remain as text (standard Markdown behavior).

## Examples

### Example 1: Marker Separation

```python
from markdown import markdown

text = """
- Item with dash
- Another dash

+ Item with plus
+ Another plus
"""

html = markdown(text, extensions=['mdx_better_lists'])

# Output: Three separate <ul> elements (blank line + marker change)
```

### Example 2: Nested Lists with Custom Indentation

```python
from markdown import markdown

text = """
- Parent
    - Nested (4 spaces)
        - Deeply nested (8 spaces)
"""

html = markdown(text, extensions=['mdx_better_lists'],
                extension_configs={'mdx_better_lists': {
                    'nested_indent': 4
                }})
```

### Example 3: Preserving List Numbers

```python
from markdown import markdown

text = """
1. Introduction
1. Background
1. Methods
"""

html = markdown(text, extensions=['mdx_better_lists'],
                extension_configs={'mdx_better_lists': {
                    'preserve_numbers': True
                }})

# Each item gets value="1"
```

### Migration from mdx_truly_sane_lists

```python
# mdx_truly_sane_lists
markdown(text, extensions=['mdx_truly_sane_lists'],
         extension_configs={'mdx_truly_sane_lists': {
             'truly_sane': True  # Default
             'nested_indent': 2  # Default
         }})

# Equivalent in mdx_better_lists (this is the default)
markdown(text, extensions=['mdx_better_lists'],
         extension_configs={'mdx_better_lists': {
             'marker_separation': True, # Default
             'unordered_list_separation': True, # Default
             'ordered_list_loose': True # Default
             'nested_indent': 2  # Default
         }})
```

**Note:** `mdx_better_lists` does not support loose list behavior (paragraph wrapping) for unordered lists. Unordered lists always remain tight, even when both `marker_separation` and `unordered_list_separation` are set to `False`.

## Development

This project follows Test-Driven Development (TDD) principles.

### Running Tests

```bash
pytest tests/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by [mdx_truly_sane_lists](https://github.com/radude/mdx_truly_sane_lists)
- Built on [Python-Markdown](https://python-markdown.github.io/)