"""Pytest configuration and fixtures for mdx_better_lists tests."""

import markdown
import pytest


@pytest.fixture
def md():
    """Create a Markdown instance with the better_lists extension."""
    return markdown.Markdown(extensions=["mdx_better_lists"])


@pytest.fixture
def md_custom():
    """Create a Markdown instance factory with custom config."""

    def _md(**kwargs):
        return markdown.Markdown(
            extensions=["mdx_better_lists"],
            extension_configs={"mdx_better_lists": kwargs},
        )

    return _md


def convert(md_instance, text):
    """Helper to convert markdown text and reset instance."""
    result = md_instance.convert(text)
    md_instance.reset()
    return result
