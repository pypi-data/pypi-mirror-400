# Sunjeet Tools

[![PyPI version](https://badge.fury.io/py/sunjeet-tools.svg)](https://pypi.org/project/sunjeet-tools/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

Personal utility library with common development tools.

## Installation

```bash
pip install sunjeet-tools
```

## Quick Start

```python
from sunjeet_tools import gacp

# Git add, commit, and push in one line
gacp(".", "Initial commit", "main")
```

## Features

- **Git Tools**: Streamlined git workflows
  - `gacp`: Git Add, Commit, Push in one command
- **Utils**: Common file and directory operations
  - JSON file operations
  - Directory utilities

## Usage

### As Library

```python
from sunjeet_tools import gacp
from sunjeet_tools.utils import read_json, write_json, ensure_dir

# Git workflow
gacp(".", "feat: add new feature", "main")

# JSON operations
data = read_json("config.json")
write_json({"key": "value"}, "output.json")

# Directory operations
ensure_dir("path/to/directory")
```

### CLI Commands

```bash
# Git add, commit, push
gacp "." "commit message" "main"
```

## Documentation

Full documentation available at: [sunjeet-tools.readthedocs.io](https://sunjeet-tools.readthedocs.io/)

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## License

MIT License - see [LICENSE](LICENSE) file for details.