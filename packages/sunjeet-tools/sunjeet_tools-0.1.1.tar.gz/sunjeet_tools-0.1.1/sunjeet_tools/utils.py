"""General utility functions."""

import os
import json


def read_json(filepath):
    """Read JSON file.
    
    Args:
        filepath (str): Path to JSON file.
    
    Returns:
        dict: Parsed JSON data.
    
    Example:
        >>> data = read_json("config.json")
    """
    with open(filepath, 'r') as f:
        return json.load(f)


def write_json(data, filepath):
    """Write data to JSON file.
    
    Args:
        data (dict): Data to write.
        filepath (str): Path to output file.
    
    Example:
        >>> write_json({"key": "value"}, "output.json")
    """
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def ensure_dir(path):
    """Ensure directory exists.
    
    Args:
        path (str): Directory path to create.
    
    Example:
        >>> ensure_dir("path/to/directory")
    """
    os.makedirs(path, exist_ok=True)