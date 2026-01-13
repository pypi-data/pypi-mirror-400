# Sunjeet Tools

Personal utility library with common development tools.

## Installation

```bash
pip install sunjeet-tools
```

## Features

### Git Tools
- `gacp`: Git Add, Commit, Push in one command

### Utils
- JSON file operations
- Directory utilities

## Usage

### As Library
```python
from sunjeet_tools import gacp

# Quick git workflow
gacp(".", "Initial commit", "main")
```

### CLI Commands
```bash
# Git add, commit, push
gacp "." "commit message" "main"
```

## License

MIT