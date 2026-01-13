"""Environment class for Luma."""

from typing import Any, Callable, Dict, Optional
from .template import Template
from .loaders import BaseLoader, FileSystemLoader
from .exceptions import TemplateNotFound


class Environment:
    """
    Luma template environment.

    Manages template loading, caching, and global configuration.

    Examples:
        >>> from luma import Environment, FileSystemLoader
        >>> env = Environment(loader=FileSystemLoader('templates'))
        >>> template = env.get_template('index.html')
        >>> template.render(title='Home')
    """

    def __init__(
        self,
        loader: Optional[BaseLoader] = None,
        syntax: str = "auto",
        autoescape: bool = True,
        cache_size: int = 400,
        **options
    ):
        """
        Create a new environment.

        Args:
            loader: Template loader instance
            syntax: Default syntax mode ("auto", "jinja", "luma")
            autoescape: Enable HTML autoescaping (default: True)
            cache_size: Maximum number of cached templates
            **options: Additional options
        """
        self.loader = loader or FileSystemLoader(".")
        self.syntax = syntax
        self.autoescape = autoescape
        self.cache_size = cache_size
        self.options = options

        self._cache: Dict[str, Template] = {}
        self._filters: Dict[str, Callable] = {}
        self._tests: Dict[str, Callable] = {}
        self._globals: Dict[str, Any] = {}

    def get_template(self, name: str, globals: Optional[Dict[str, Any]] = None) -> Template:
        """
        Load a template by name.

        Args:
            name: Template name/path
            globals: Additional global variables

        Returns:
            Compiled Template instance

        Raises:
            TemplateNotFound: If template doesn't exist
        """
        # Check cache
        if name in self._cache:
            return self._cache[name]

        # Load from loader
        source = self.loader.get_source(name)
        if source is None:
            raise TemplateNotFound(f"Template not found: {name}")

        # Compile template
        template = Template(source, syntax=self.syntax)

        # Cache if enabled
        if self.cache_size > 0:
            if len(self._cache) >= self.cache_size:
                # Simple LRU: remove first item
                self._cache.pop(next(iter(self._cache)))
            self._cache[name] = template

        return template

    def from_string(self, source: str) -> Template:
        """
        Create template from string.

        Args:
            source: Template source code

        Returns:
            Compiled Template instance
        """
        return Template(source, syntax=self.syntax)

    def add_filter(self, name: str, func: Callable):
        """
        Add a custom filter.

        Args:
            name: Filter name
            func: Filter function

        Examples:
            >>> def reverse(s):
            ...     return s[::-1]
            >>> env.add_filter('reverse', reverse)
        """
        self._filters[name] = func

    def add_test(self, name: str, func: Callable):
        """
        Add a custom test.

        Args:
            name: Test name
            func: Test function (returns bool)

        Examples:
            >>> def is_prime(n):
            ...     return n > 1 and all(n % i for i in range(2, int(n**0.5) + 1))
            >>> env.add_test('prime', is_prime)
        """
        self._tests[name] = func

    def add_global(self, name: str, value: Any):
        """
        Add a global variable available to all templates.

        Args:
            name: Variable name
            value: Variable value
        """
        self._globals[name] = value

    def clear_cache(self):
        """Clear the template cache."""
        self._cache.clear()

    def __repr__(self) -> str:
        """String representation."""
        return f"<Environment loader={self.loader!r}>"
