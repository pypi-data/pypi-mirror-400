"""General utility functions."""

import os
import json


def read_json(filepath):
    """Read JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def write_json(data, filepath):
    """Write data to JSON file."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def ensure_dir(path):
    """Ensure directory exists."""
    os.makedirs(path, exist_ok=True)