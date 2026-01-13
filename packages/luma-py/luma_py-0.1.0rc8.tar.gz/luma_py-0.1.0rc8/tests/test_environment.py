"""Tests for Environment class."""

import os
import tempfile
import pytest
from luma import Environment, FileSystemLoader, DictLoader
from luma.exceptions import TemplateNotFound


def test_environment_basic():
    """Test basic Environment creation."""
    env = Environment()
    assert env is not None


def test_environment_from_string():
    """Test creating template from string."""
    env = Environment()
    template = env.from_string("Hello, {{ name }}!")
    result = template.render(name="World")
    assert result == "Hello, World!"


def test_environment_with_dict_loader():
    """Test Environment with DictLoader."""
    templates = {
        "hello.html": "Hello, {{ name }}!",
        "goodbye.html": "Goodbye, {{ name }}!",
    }
    env = Environment(loader=DictLoader(templates))

    template = env.get_template("hello.html")
    assert template.render(name="Alice") == "Hello, Alice!"

    template = env.get_template("goodbye.html")
    assert template.render(name="Bob") == "Goodbye, Bob!"


def test_environment_with_filesystem_loader():
    """Test Environment with FileSystemLoader."""
    # Create temporary directory with templates
    with tempfile.TemporaryDirectory() as tmpdir:
        # Write test templates
        with open(os.path.join(tmpdir, "test.html"), "w") as f:
            f.write("Hello, {{ name }}!")

        # Load with FileSystemLoader
        env = Environment(loader=FileSystemLoader(tmpdir))
        template = env.get_template("test.html")
        result = template.render(name="Test")
        assert result == "Hello, Test!"


def test_environment_template_not_found():
    """Test TemplateNotFound exception."""
    templates = {"exists.html": "Content"}
    env = Environment(loader=DictLoader(templates))

    with pytest.raises(TemplateNotFound):
        env.get_template("does_not_exist.html")


def test_environment_custom_filter():
    """Test adding custom filter."""
    env = Environment()

    # Add custom filter
    env.add_filter("reverse", lambda s: s[::-1])

    template = env.from_string("{{ text | reverse }}")
    result = template.render(text="hello")
    assert result == "olleh"


def test_environment_custom_test():
    """Test adding custom test."""
    env = Environment()

    # Add custom test
    env.add_test("even", lambda n: n % 2 == 0)

    template = env.from_string("{% if num is even %}even{% else %}odd{% endif %}")
    assert "even" in template.render(num=4)
    assert "odd" in template.render(num=3)


def test_environment_shared_runtime():
    """Test templates sharing runtime."""
    env = Environment()

    # Both templates should use shared runtime
    template1 = env.from_string("{{ value }}")
    template2 = env.from_string("{{ value * 2 }}")

    assert template1.render(value=5) == "5"
    assert template2.render(value=5) == "10"


def test_environment_autoescape():
    """Test autoescape setting."""
    env = Environment(autoescape=True)
    template = env.from_string("{{ html }}")
    result = template.render(html="<script>alert('xss')</script>")
    # Should be escaped
    assert "&lt;" in result or "<" not in result


def test_environment_multiple_search_paths():
    """Test FileSystemLoader with multiple search paths."""
    with tempfile.TemporaryDirectory() as tmpdir1:
        with tempfile.TemporaryDirectory() as tmpdir2:
            # Create templates in different directories
            with open(os.path.join(tmpdir1, "template1.html"), "w") as f:
                f.write("Template 1")
            with open(os.path.join(tmpdir2, "template2.html"), "w") as f:
                f.write("Template 2")

            # Load from multiple paths
            env = Environment(loader=FileSystemLoader([tmpdir1, tmpdir2]))

            template1 = env.get_template("template1.html")
            template2 = env.get_template("template2.html")

            assert "Template 1" in template1.render()
            assert "Template 2" in template2.render()
