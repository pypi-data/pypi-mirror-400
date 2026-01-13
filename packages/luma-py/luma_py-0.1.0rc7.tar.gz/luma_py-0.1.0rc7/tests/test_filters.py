"""Tests for template filters."""

import pytest
from luma import Template


def test_upper_filter():
    """Test upper filter."""
    template = Template("{{ text | upper }}")
    result = template.render(text="hello")
    assert result == "HELLO"


def test_lower_filter():
    """Test lower filter."""
    template = Template("{{ text | lower }}")
    result = template.render(text="HELLO")
    assert result == "hello"


def test_default_filter():
    """Test default filter."""
    template = Template("{{ value | default('fallback') }}")
    assert template.render(value="exists") == "exists"
    assert template.render() == "fallback"


def test_length_filter():
    """Test length filter."""
    template = Template("{{ items | length }}")
    result = template.render(items=[1, 2, 3, 4, 5])
    assert "5" in result


def test_join_filter():
    """Test join filter."""
    template = Template("{{ items | join(', ') }}")
    result = template.render(items=["apple", "banana", "cherry"])
    assert "apple" in result
    assert "banana" in result
    assert ", " in result


def test_filter_chaining():
    """Test chaining multiple filters."""
    template = Template("{{ text | upper | reverse }}")
    result = template.render(text="hello")
    # Result should be "OLLEH" (hello -> HELLO -> OLLEH)
    assert "OLLEH" in result or "olleh" in result.lower()


def test_first_filter():
    """Test first filter."""
    template = Template("{{ items | first }}")
    result = template.render(items=["apple", "banana", "cherry"])
    assert "apple" in result


def test_last_filter():
    """Test last filter."""
    template = Template("{{ items | last }}")
    result = template.render(items=["apple", "banana", "cherry"])
    assert "cherry" in result


def test_safe_filter():
    """Test safe filter (marks content as safe HTML)."""
    template = Template("{{ html | safe }}")
    result = template.render(html="<b>bold</b>")
    assert "<b>" in result
    assert "bold" in result


def test_escape_filter():
    """Test escape filter."""
    template = Template("{{ html | escape }}")
    result = template.render(html="<script>alert('xss')</script>")
    assert "&lt;" in result or "<" not in result
