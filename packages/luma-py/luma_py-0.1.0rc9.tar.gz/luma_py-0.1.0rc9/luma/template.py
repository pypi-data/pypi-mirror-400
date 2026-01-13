"""Template class for Luma."""

import os
from typing import Any, Dict, Optional
from lupa import LuaRuntime

from .exceptions import TemplateError, TemplateSyntaxError


class Template:
    """
    A compiled Luma template.

    Examples:
        >>> template = Template("Hello, {{ name }}!")
        >>> template.render(name="World")
        'Hello, World!'

        >>> template = Template.from_file("template.luma")
        >>> template.render(user="Alice")
    """

    def __init__(self, source: str, syntax: str = "auto", lua_runtime: Optional[LuaRuntime] = None):
        """
        Create a template from source string.

        Args:
            source: Template source code
            syntax: Syntax mode - "auto", "jinja", or "luma" (default: "auto")
            lua_runtime: Optional shared LuaRuntime instance

        Raises:
            TemplateSyntaxError: If template has syntax errors
        """
        self.source = source
        self.syntax = syntax
        self._lua = lua_runtime or LuaRuntime(unpack_returned_tuples=True)
        self._luma_initialized = lua_runtime is not None
        self._compiled = None
        self._compile()

    def _compile(self):
        """Compile the template using Luma's Lua engine."""
        try:
            # Initialize Luma modules if not already done
            if not self._luma_initialized:
                # Get the path to Luma's Lua modules (relative to this Python file)
                bindings_dir = os.path.dirname(os.path.abspath(__file__))
                luma_root = os.path.join(bindings_dir, '../../..')
                luma_root = os.path.abspath(luma_root)
                # Convert to forward slashes for Lua (works on Windows too)
                luma_root = luma_root.replace('\\', '/')

                # Set up Lua package path to find Luma modules (prepend to take precedence)
                package_path_setup = f"""
                    package.path = '{luma_root}/?.lua;{luma_root}/?/init.lua;' .. package.path
                    luma = require('luma')
                    filters = require('luma.filters')
                    runtime = require('luma.runtime')
                """
                self._lua.execute(package_path_setup)
                self._luma_initialized = True

            # Get references to Lua modules
            self._luma = self._lua.globals().luma
            self._filters = self._lua.globals().filters
            self._runtime = self._lua.globals().runtime

            # Compile template
            options = self._lua.table(syntax=self.syntax, no_jinja_warning=True)
            self._compiled = self._luma.compile(
                self.source,
                options
            )

        except Exception as e:
            raise TemplateSyntaxError(f"Failed to compile template: {e}")

    def render(self, **context) -> str:
        """
        Render the template with given context.

        Args:
            **context: Template variables as keyword arguments

        Returns:
            Rendered template string

        Raises:
            TemplateError: If rendering fails

        Examples:
            >>> template.render(name="Alice", age=30)
            'Name: Alice, Age: 30'
        """
        return self.render_dict(context)

    def _python_to_lua(self, obj: Any) -> Any:
        """Recursively convert Python objects to Lua types."""
        if isinstance(obj, dict):
            lua_table = self._lua.table()
            for k, v in obj.items():
                lua_table[k] = self._python_to_lua(v)
            return lua_table
        elif isinstance(obj, (list, tuple)):
            lua_table = self._lua.table()
            for i, item in enumerate(obj, 1):  # Lua arrays are 1-indexed
                lua_table[i] = self._python_to_lua(item)
            return lua_table
        else:
            return obj

    def render_dict(self, context: Dict[str, Any]) -> str:
        """
        Render the template with context dictionary.

        Args:
            context: Template variables as dictionary

        Returns:
            Rendered template string

        Raises:
            TemplateError: If rendering fails
        """
        if not self._compiled:
            raise TemplateError("Template not compiled")

        try:
            # Convert Python dict to Lua table (with recursive conversion)
            lua_context = self._python_to_lua(context)

            # Get filters
            all_filters = self._filters.get_all()

            # Render template with proper arguments
            # Note: We need to store references in Lua global space and use colon operator
            g = self._lua.globals()
            g._template_to_render = self._compiled
            g._ctx_to_use = lua_context
            g._filters_to_use = all_filters
            g._runtime_to_use = self._runtime

            result = self._lua.execute("return _template_to_render:render(_ctx_to_use, _filters_to_use, _runtime_to_use)")

            return str(result)

        except Exception as e:
            raise TemplateError(f"Failed to render template: {e}")

    @classmethod
    def from_file(cls, path: str, syntax: str = "auto", encoding: str = "utf-8") -> "Template":
        """
        Load template from file.

        Args:
            path: Path to template file
            syntax: Syntax mode - "auto", "jinja", or "luma"
            encoding: File encoding (default: "utf-8")

        Returns:
            Compiled Template instance

        Raises:
            FileNotFoundError: If template file doesn't exist
            TemplateSyntaxError: If template has syntax errors

        Examples:
            >>> template = Template.from_file("templates/index.html")
            >>> template.render(title="Home")
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Template not found: {path}")

        with open(path, "r", encoding=encoding) as f:
            source = f.read()

        return cls(source, syntax=syntax)

    def __repr__(self) -> str:
        """String representation of template."""
        preview = self.source[:50].replace("\n", "\\n")
        if len(self.source) > 50:
            preview += "..."
        return f'<Template source="{preview}">'
