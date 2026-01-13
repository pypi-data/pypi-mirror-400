"""
Utility functions for Envy.
"""

import os
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


def find_envy_root(start_path: Optional[str] = None) -> Optional[str]:
    """
    Find the root directory containing .envy folder.
    Walks up the directory tree from start_path.
    """
    if start_path is None:
        start_path = os.getcwd()
    
    current = Path(start_path).resolve()
    
    while current != current.parent:
        if (current / ".envy").is_dir():
            return str(current)
        current = current.parent
    
    # Check root as well
    if (current / ".envy").is_dir():
        return str(current)
    
    return None


def is_envy_initialized(path: Optional[str] = None) -> bool:
    """Check if envy is initialized in the current or specified directory."""
    if path is None:
        path = os.getcwd()
    
    envy_dir = os.path.join(path, ".envy")
    master_key = os.path.join(envy_dir, "master.key")
    
    return os.path.exists(envy_dir) and os.path.exists(master_key)


def get_gitignore_path() -> str:
    """Get the path to .gitignore file."""
    return os.path.join(os.getcwd(), ".gitignore")


def ensure_gitignore_entry(entry: str) -> bool:
    """
    Ensure an entry exists in .gitignore.
    Creates the file if it doesn't exist, appends if it does.
    Returns True if entry was added, False if it already existed.
    """
    gitignore_path = get_gitignore_path()
    
    # Read existing content
    existing_entries = set()
    file_exists = os.path.exists(gitignore_path)
    
    if file_exists:
        with open(gitignore_path, "r") as f:
            existing_entries = set(line.strip() for line in f if line.strip())
    
    # Check if entry already exists
    if entry in existing_entries:
        return False
    
    # Add entry
    mode = "a" if file_exists else "w"
    with open(gitignore_path, mode) as f:
        # Add newline before entry if file exists and doesn't end with newline
        if file_exists:
            f.write(f"{entry}\n")
        else:
            # New file - add header comment
            if entry.startswith("#"):
                f.write(f"{entry}\n")
            else:
                f.write(f"{entry}\n")
    
    return True


def format_timestamp(timestamp: str) -> str:
    """Format an ISO timestamp for display."""
    try:
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return timestamp


def format_relative_time(timestamp: str) -> str:
    """Format a timestamp as relative time (e.g., '2 days ago')."""
    try:
        dt = datetime.fromisoformat(timestamp)
        now = datetime.now()
        delta = now - dt
        
        if delta.days > 365:
            years = delta.days // 365
            return f"{years} year{'s' if years > 1 else ''} ago"
        elif delta.days > 30:
            months = delta.days // 30
            return f"{months} month{'s' if months > 1 else ''} ago"
        elif delta.days > 0:
            return f"{delta.days} day{'s' if delta.days > 1 else ''} ago"
        elif delta.seconds > 3600:
            hours = delta.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif delta.seconds > 60:
            minutes = delta.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "just now"
    except (ValueError, TypeError):
        return timestamp


def mask_secret(value: str, show_chars: int = 4) -> str:
    """Mask a secret value for display."""
    if len(value) <= show_chars * 2:
        return "*" * len(value)
    
    return value[:show_chars] + "*" * (len(value) - show_chars * 2) + value[-show_chars:]


def parse_key_value(kv_string: str) -> tuple[str, str]:
    """Parse a KEY=VALUE string."""
    if "=" not in kv_string:
        raise ValueError(f"Invalid format: '{kv_string}'. Expected KEY=VALUE")
    
    key, _, value = kv_string.partition("=")
    return key.strip(), value.strip()


def parse_expiry(expiry_str: str) -> int:
    """
    Parse an expiry string like '30d', '2w', '6m' to days.
    Supported units: d (days), w (weeks), m (months), y (years)
    """
    expiry_str = expiry_str.strip().lower()
    
    if expiry_str.endswith("d"):
        return int(expiry_str[:-1])
    elif expiry_str.endswith("w"):
        return int(expiry_str[:-1]) * 7
    elif expiry_str.endswith("m"):
        return int(expiry_str[:-1]) * 30
    elif expiry_str.endswith("y"):
        return int(expiry_str[:-1]) * 365
    else:
        # Assume days if no unit specified
        return int(expiry_str)


def get_shell_export_command(key: str, value: str) -> str:
    """Get the appropriate export command for the current shell."""
    if sys.platform == "win32":
        # PowerShell
        escaped_value = value.replace("'", "''")
        return f"$env:{key}='{escaped_value}'"
    else:
        # Bash/Zsh
        escaped_value = value.replace("'", "'\"'\"'")
        return f"export {key}='{escaped_value}'"


def get_platform_info() -> dict:
    """Get information about the current platform."""
    return {
        "platform": sys.platform,
        "python_version": sys.version,
        "cwd": os.getcwd(),
    }


def validate_profile_name(name: str) -> tuple[bool, str]:
    """Validate a profile name."""
    if not name:
        return False, "Profile name cannot be empty"
    
    if not name[0].isalpha():
        return False, "Profile name must start with a letter"
    
    if not all(c.isalnum() or c in "-_" for c in name):
        return False, "Profile name can only contain letters, numbers, hyphens, and underscores"
    
    if len(name) > 50:
        return False, "Profile name must be 50 characters or less"
    
    return True, ""


def validate_key_name(name: str) -> tuple[bool, str]:
    """Validate an environment variable key name."""
    if not name:
        return False, "Key name cannot be empty"
    
    if not name[0].isalpha() and name[0] != "_":
        return False, "Key name must start with a letter or underscore"
    
    if not all(c.isalnum() or c == "_" for c in name):
        return False, "Key name can only contain letters, numbers, and underscores"
    
    # Convention: env vars are usually uppercase
    if name != name.upper():
        # This is a warning, not an error
        pass
    
    return True, ""
