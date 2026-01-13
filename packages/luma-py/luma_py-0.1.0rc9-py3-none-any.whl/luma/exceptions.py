"""Exceptions for Luma."""


class TemplateError(Exception):
    """Base exception for all template errors."""
    pass


class TemplateSyntaxError(TemplateError):
    """Raised when template has syntax errors."""
    pass


class TemplateNotFound(TemplateError):
    """Raised when template file is not found."""
    pass


class TemplateRuntimeError(TemplateError):
    """Raised when template rendering fails."""
    pass


class UndefinedError(TemplateRuntimeError):
    """Raised when accessing undefined variables (if strict mode enabled)."""
    pass
