"""Template loaders for Luma."""

import os
from typing import Optional, Dict
from abc import ABC, abstractmethod


class BaseLoader(ABC):
    """Base class for template loaders."""

    @abstractmethod
    def get_source(self, name: str) -> Optional[str]:
        """
        Get template source by name.

        Args:
            name: Template name/path

        Returns:
            Template source code or None if not found
        """
        pass


class FileSystemLoader(BaseLoader):
    """
    Load templates from filesystem.

    Examples:
        >>> loader = FileSystemLoader('templates')
        >>> loader = FileSystemLoader(['templates', 'includes'])
    """

    def __init__(self, searchpath, encoding='utf-8'):
        """
        Create filesystem loader.

        Args:
            searchpath: Directory or list of directories to search
            encoding: File encoding (default: 'utf-8')
        """
        if isinstance(searchpath, str):
            searchpath = [searchpath]
        self.searchpath = searchpath
        self.encoding = encoding

    def get_source(self, name: str) -> Optional[str]:
        """Load template from filesystem."""
        for path in self.searchpath:
            filename = os.path.join(path, name)
            if os.path.exists(filename):
                with open(filename, 'r', encoding=self.encoding) as f:
                    return f.read()
        return None

    def __repr__(self) -> str:
        return f"<FileSystemLoader searchpath={self.searchpath!r}>"


class DictLoader(BaseLoader):
    """
    Load templates from dictionary.

    Useful for testing or pre-compiled templates.

    Examples:
        >>> templates = {
        ...     'index.html': '<h1>{{ title }}</h1>',
        ...     'about.html': '<p>About page</p>',
        ... }
        >>> loader = DictLoader(templates)
    """

    def __init__(self, templates: Dict[str, str]):
        """
        Create dict loader.

        Args:
            templates: Dictionary mapping names to source code
        """
        self.templates = templates

    def get_source(self, name: str) -> Optional[str]:
        """Load template from dictionary."""
        return self.templates.get(name)

    def __repr__(self) -> str:
        return f"<DictLoader templates={list(self.templates.keys())!r}>"


class PackageLoader(BaseLoader):
    """
    Load templates from Python package.

    Examples:
        >>> loader = PackageLoader('myapp', 'templates')
    """

    def __init__(self, package_name: str, package_path: str = 'templates'):
        """
        Create package loader.

        Args:
            package_name: Python package name
            package_path: Path within package (default: 'templates')
        """
        self.package_name = package_name
        self.package_path = package_path

        # Get package directory
        import importlib
        try:
            package = importlib.import_module(package_name)
            if package.__file__ is None:
                raise ValueError(f"Package {package_name} has no __file__ attribute (possibly a namespace package)")
            self.search_path = os.path.join(
                os.path.dirname(package.__file__),
                package_path
            )
        except ImportError:
            raise ValueError(f"Package not found: {package_name}")

    def get_source(self, name: str) -> Optional[str]:
        """Load template from package."""
        filename = os.path.join(self.search_path, name)
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return f.read()
        return None

    def __repr__(self) -> str:
        return f"<PackageLoader package={self.package_name!r} path={self.package_path!r}>"
