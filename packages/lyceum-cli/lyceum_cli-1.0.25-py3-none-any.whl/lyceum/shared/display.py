"""Display utilities for CLI output formatting"""

from datetime import datetime

from rich.table import Table


def create_table(title: str, columns: list[tuple[str, str]]) -> Table:
    """
    Create a Rich table with the given title and columns.

    Args:
        title: Table title
        columns: List of (column_name, style) tuples

    Returns:
        Rich Table instance
    """
    table = Table(title=title)
    for col_name, style in columns:
        table.add_column(col_name, style=style)
    return table


def format_timestamp(timestamp: str | int | datetime, relative: bool = False) -> str:
    """
    Format a timestamp for display.

    Args:
        timestamp: Unix timestamp (int/float), ISO string, or datetime object
        relative: If True, show relative time (e.g., "2 hours ago")

    Returns:
        Formatted timestamp string
    """
    try:
        # Convert to datetime if needed
        if isinstance(timestamp, (int, float)):
            dt = datetime.fromtimestamp(timestamp)
        elif isinstance(timestamp, str):
            # Try parsing ISO format
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        elif isinstance(timestamp, datetime):
            dt = timestamp
        else:
            return str(timestamp)

        if relative:
            # Calculate relative time
            now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
            diff = now - dt

            seconds = diff.total_seconds()
            if seconds < 60:
                return f"{int(seconds)}s ago"
            elif seconds < 3600:
                return f"{int(seconds / 60)}m ago"
            elif seconds < 86400:
                return f"{int(seconds / 3600)}h ago"
            elif seconds < 604800:
                return f"{int(seconds / 86400)}d ago"
            else:
                return dt.strftime("%Y-%m-%d")
        else:
            # Return absolute time
            return dt.strftime("%Y-%m-%d %H:%M:%S")

    except Exception:
        return str(timestamp)


def truncate_id(id_str: str, length: int = 8) -> str:
    """
    Truncate an ID string for display.

    Args:
        id_str: The ID string to truncate
        length: Number of characters to keep from the start

    Returns:
        Truncated ID string
    """
    if not id_str:
        return ""

    if len(id_str) <= length:
        return id_str

    return f"{id_str[:length]}..."


def format_file_size(bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        bytes: Size in bytes

    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024.0:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.1f} PB"


def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string (e.g., "2h 15m 30s")
    """
    if seconds < 60:
        return f"{seconds:.1f}s"

    minutes = int(seconds / 60)
    secs = int(seconds % 60)

    if minutes < 60:
        return f"{minutes}m {secs}s"

    hours = int(minutes / 60)
    mins = int(minutes % 60)

    if hours < 24:
        return f"{hours}h {mins}m"

    days = int(hours / 24)
    hrs = int(hours % 24)

    return f"{days}d {hrs}h"


def status_color(status: str) -> str:
    """
    Get color for status display.

    Args:
        status: Status string

    Returns:
        Color name for Rich formatting
    """
    status_lower = status.lower()

    if status_lower in ['completed', 'success', 'running']:
        return 'green'
    elif status_lower in ['failed', 'error', 'failed_user', 'failed_system']:
        return 'red'
    elif status_lower in ['pending', 'queued', 'in_progress', 'validating', 'finalizing']:
        return 'yellow'
    elif status_lower in ['cancelled', 'expired', 'timeout']:
        return 'dim'
    else:
        return 'white'


def status_emoji(status: str) -> str:
    """
    Get emoji for status display.

    Args:
        status: Status string

    Returns:
        Emoji character
    """
    status_lower = status.lower()

    if status_lower in ['completed', 'success']:
        return '✅'
    elif status_lower in ['failed', 'error', 'failed_user', 'failed_system']:
        return '❌'
    elif status_lower in ['running', 'in_progress']:
        return '🔄'
    elif status_lower in ['pending', 'queued']:
        return '⏳'
    elif status_lower in ['validating']:
        return '🔍'
    elif status_lower in ['finalizing']:
        return '📦'
    elif status_lower in ['cancelled']:
        return '🛑'
    elif status_lower in ['expired', 'timeout']:
        return '⏰'
    else:
        return '⚪'
