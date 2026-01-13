"""Git utility functions."""

import subprocess
import sys


def gacp(files=".", commit_message=None, branch="main"):
    """Git Add, Commit, Push in one command.
    
    Args:
        files: Files to add (default: ".")
        commit_message: Commit message
        branch: Branch to push to (default: "main")
    """
    if not commit_message:
        print("Error: Commit message is required")
        return False
    
    try:
        subprocess.run(["git", "add", files], check=True)
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        subprocess.run(["git", "push", "origin", branch], check=True)
        print("✅ Successfully added, committed, and pushed")
        return True
    except subprocess.CalledProcessError:
        print("❌ Git command failed")
        return False