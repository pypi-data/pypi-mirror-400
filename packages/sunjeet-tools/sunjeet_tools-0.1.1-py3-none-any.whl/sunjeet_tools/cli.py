"""CLI entry points."""

import sys
from .git_tools import gacp


def gacp_main():
    """CLI entry point for gacp command."""
    if len(sys.argv) != 4:
        print('Usage: gacp "files" "commit message" "branch"')
        sys.exit(1)

    files = sys.argv[1]
    commit_message = sys.argv[2]
    branch = sys.argv[3]

    success = gacp(files, commit_message, branch)
    if not success:
        sys.exit(1)