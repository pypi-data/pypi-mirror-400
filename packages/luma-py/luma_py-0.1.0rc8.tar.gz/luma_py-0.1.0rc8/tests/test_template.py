"""Tests for Template class."""

import pytest
from luma import Template
from luma.exceptions import TemplateSyntaxError, TemplateError


def test_simple_render():
    """Test basic template rendering."""
    template = Template("Hello, {{ name }}!")
    result = template.render(name="World")
    assert result == "Hello, World!"


def test_luma_syntax():
    """Test Luma native syntax."""
    template = Template("Hello, $name!", syntax="luma")
    result = template.render(name="Alice")
    assert result == "Hello, Alice!"


def test_jinja_syntax():
    """Test Jinja2 syntax."""
    template = Template("{{ items | length }}", syntax="jinja")
    result = template.render(items=[1, 2, 3])
    assert "3" in result


def test_render_dict():
    """Test render_dict method."""
    template = Template("$x + $y = $z")
    result = template.render_dict({"x": 1, "y": 2, "z": 3})
    assert "1 + 2 = 3" in result


def test_complex_template():
    """Test complex template with loops."""
    source = """
    {% for item in items %}
    - {{ item }}
    {% endfor %}
    """
    template = Template(source)
    result = template.render(items=["apple", "banana", "cherry"])
    assert "apple" in result
    assert "banana" in result
    assert "cherry" in result


def test_template_repr():
    """Test template string representation."""
    template = Template("Hello")
    repr_str = repr(template)
    assert "Template" in repr_str
    assert "Hello" in repr_str
