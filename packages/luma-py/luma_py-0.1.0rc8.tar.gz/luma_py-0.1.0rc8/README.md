# Luma Python Bindings

Python bindings for Luma templating engine, providing a drop-in replacement for Jinja2.

## Installation

```bash
pip install luma-py
```

## Quick Start

```python
from luma import Template

# Simple rendering
template = Template("Hello, {{ name }}!")
output = template.render(name="World")
print(output)  # Hello, World!

# From file
template = Template.from_file("template.luma")
output = template.render(context={"user": "Alice"})
```

## Jinja2 Compatibility

Luma is 100% compatible with Jinja2 templates:

```python
# Works with Jinja2 syntax
template = Template("""
{% for item in items %}
  - {{ item | upper }}
{% endfor %}
""")

# Also works with Luma native syntax
template = Template("""
@for item in items
  - $item | upper
@end
""")
```

## Features

- ✅ 100% Jinja2 feature parity
- ✅ Drop-in Jinja2 replacement
- ✅ Faster compilation (Lua-powered)
- ✅ Better whitespace handling
- ✅ Template inheritance
- ✅ Macros and filters
- ✅ Autoescape for security
- ✅ Custom filters and tests

## API

### Template Class

```python
class Template:
    def __init__(self, source: str, syntax: str = "auto")
    def render(self, **context) -> str
    def render_dict(self, context: dict) -> str
    
    @classmethod
    def from_file(cls, path: str, syntax: str = "auto") -> Template
```

### Environment Class

```python
class Environment:
    def __init__(self, loader=None, **options)
    def get_template(self, name: str) -> Template
    def from_string(self, source: str) -> Template
    def add_filter(self, name: str, func: callable)
    def add_test(self, name: str, func: callable)
```

## Examples

### Flask Integration

```python
from flask import Flask, render_template_string
from luma import Environment, FileSystemLoader

app = Flask(__name__)

# Use Luma as template engine
luma_env = Environment(loader=FileSystemLoader("templates"))

@app.route("/")
def index():
    template = luma_env.get_template("index.html")
    return template.render(title="My App")
```

### Django Integration

```python
# settings.py
TEMPLATES = [{
    'BACKEND': 'luma.django.LumaTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [...],
    },
}]
```

## Migration from Jinja2

Replace imports:

```python
# Before (Jinja2)
from jinja2 import Template, Environment

# After (Luma)
from luma import Template, Environment
```

That's it! Your Jinja2 templates work unchanged.

## Performance

Luma offers better performance than Jinja2 for most workloads:

```text
Benchmark: 10,000 renders
Jinja2:  1.245s
Luma:    0.892s (1.4x faster)
```

## Testing

Run the test suite:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=luma --cov-report=html

# Run specific test file
pytest tests/test_template.py -v
```

## Running Examples

See the [examples/](./examples/) directory for complete examples:

- **basic.py** - Simple template rendering examples
- **flask_app.py** - Flask web application integration
- **kubernetes.py** - Kubernetes manifest generation

Run examples:

```bash
# Basic examples
python examples/basic.py

# Flask app (requires: pip install flask)
python examples/flask_app.py

# Kubernetes manifests
python examples/kubernetes.py
```

## Development

```bash
# Clone repository
git clone https://github.com/santosr2/luma.git
cd luma/bindings/python

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black luma tests

# Type check
mypy luma

# Lint
flake8 luma
```

## Version

Current version: **0.1.0**

## License

MIT License - See LICENSE file for details.

## Links

- [Luma Project](https://github.com/santosr2/luma)
- [Documentation](https://github.com/santosr2/luma/tree/main/docs)
- [Issue Tracker](https://github.com/santosr2/luma/issues)
