"""Core functionality for finding large files and directories using pure Python."""

from __future__ import annotations

import fnmatch
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterator

# Size units in bytes for parsing and filtering
SIZE_UNITS = {
    "B": 1,
    "K": 1024,
    "M": 1024**2,
    "G": 1024**3,
    "T": 1024**4,
    "P": 1024**5,
}


@dataclass
class SizeEntry:
    """Represents a file or directory with its size."""

    path: str
    size_bytes: int
    size_human: str = field(default="")

    def __post_init__(self):
        if not self.size_human:
            self.size_human = format_size(self.size_bytes)

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "size_human": self.size_human,
            "size_bytes": self.size_bytes,
        }


def parse_size(size_str: str) -> int:
    """Parse human-readable size string to bytes.

    Args:
        size_str: Size string like '1.5G', '100M', '500K', '1024'

    Returns:
        Size in bytes
    """
    size_str = size_str.strip().upper()

    # Handle plain numbers (bytes)
    if size_str.isdigit():
        return int(size_str)

    # Match number with optional decimal and unit
    match = re.match(r"^([\d.]+)\s*([BKMGTP])?I?B?$", size_str)
    if not match:
        raise ValueError(f"Cannot parse size: {size_str}")

    value = float(match.group(1))
    unit = match.group(2) or "B"

    return int(value * SIZE_UNITS[unit])


def format_size(size_bytes: int) -> str:
    """Format bytes as human-readable string."""
    for unit in ["B", "K", "M", "G", "T", "P"]:
        if abs(size_bytes) < 1024:
            if unit == "B":
                return f"{size_bytes}{unit}"
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f}P"


def should_exclude(path: Path, excludes: list[str]) -> bool:
    """Check if a path should be excluded based on patterns."""
    name = path.name
    path_str = str(path)

    for pattern in excludes:
        # Check if name matches pattern
        if fnmatch.fnmatch(name, pattern):
            return True
        # Check if any part of the path matches
        if pattern in path_str.split(os.sep):
            return True
    return False


def count_items(
    directory: Path,
    count_files: bool = True,
    excludes: list[str] | None = None,
) -> int:
    """Count files or directories for progress tracking.

    Args:
        directory: Directory to scan
        count_files: If True count files, if False count dirs at depth 1
        excludes: Patterns to exclude

    Returns:
        Count of items
    """
    excludes = excludes or []
    count = 0

    if count_files:
        for root, dirs, files in os.walk(directory):
            root_path = Path(root)

            # Filter out excluded directories (modifies dirs in-place to skip them)
            dirs[:] = [d for d in dirs if not should_exclude(root_path / d, excludes)]

            for f in files:
                file_path = root_path / f
                if not should_exclude(file_path, excludes):
                    count += 1
    else:
        # For directories, just count immediate children
        try:
            for item in directory.iterdir():
                if item.is_dir() and not should_exclude(item, excludes):
                    count += 1
        except PermissionError:
            pass

    return count


def get_file_size(path: Path, apparent: bool = False) -> int:
    """Get file size, returning 0 on error.

    Args:
        path: File path
        apparent: If True, return apparent size (st_size).
                  If False, return actual disk usage (st_blocks * 512).
    """
    try:
        stat = path.stat()
        if apparent:
            return stat.st_size
        # st_blocks is number of 512-byte blocks allocated
        # This gives actual disk usage, accounting for sparse files,
        # hard links, and APFS clones
        return stat.st_blocks * 512
    except (OSError, PermissionError, AttributeError):
        # AttributeError: st_blocks not available on Windows
        try:
            return path.stat().st_size
        except (OSError, PermissionError):
            return 0


def get_dir_size(path: Path, excludes: list[str] | None = None) -> int:
    """Calculate total size of a directory recursively."""
    excludes = excludes or []
    total = 0

    try:
        for root, dirs, files in os.walk(path):
            root_path = Path(root)

            # Filter excluded directories
            dirs[:] = [d for d in dirs if not should_exclude(root_path / d, excludes)]

            for f in files:
                file_path = root_path / f
                if not should_exclude(file_path, excludes):
                    total += get_file_size(file_path)
    except PermissionError:
        pass

    return total


def find_large_files(
    directory: str | Path = ".",
    limit: int = 10,
    excludes: list[str] | None = None,
    min_size: int | None = None,
    progress_callback: Callable[[int, int], None] | None = None,
) -> list[SizeEntry]:
    """Find the largest files in a directory.

    Args:
        directory: Directory to search
        limit: Maximum number of results (0 for unlimited)
        excludes: Patterns to exclude
        min_size: Minimum size in bytes to include
        progress_callback: Called with (current, total) for progress updates

    Returns:
        List of SizeEntry objects sorted by size descending
    """
    directory = Path(directory).resolve()
    if not directory.is_dir():
        raise NotADirectoryError(f"Not a directory: {directory}")

    excludes = excludes or []
    entries: list[SizeEntry] = []

    # Count files first for progress
    total_files = 0
    if progress_callback:
        total_files = count_items(directory, count_files=True, excludes=excludes)

    current = 0
    for root, dirs, files in os.walk(directory):
        root_path = Path(root)

        # Filter out excluded directories
        dirs[:] = [d for d in dirs if not should_exclude(root_path / d, excludes)]

        for f in files:
            file_path = root_path / f

            if should_exclude(file_path, excludes):
                continue

            size = get_file_size(file_path)

            if min_size is not None and size < min_size:
                current += 1
                if progress_callback:
                    progress_callback(current, total_files)
                continue

            entries.append(SizeEntry(path=str(file_path), size_bytes=size))

            current += 1
            if progress_callback:
                progress_callback(current, total_files)

    # Sort by size descending
    entries.sort(key=lambda e: e.size_bytes, reverse=True)

    # Apply limit
    if limit > 0:
        entries = entries[:limit]

    return entries


def find_large_dirs(
    directory: str | Path = ".",
    limit: int = 10,
    depth: int = 1,
    excludes: list[str] | None = None,
    min_size: int | None = None,
    progress_callback: Callable[[int, int], None] | None = None,
) -> list[SizeEntry]:
    """Find the largest directories.

    Args:
        directory: Directory to search
        limit: Maximum number of results (0 for unlimited)
        depth: How deep to go (1 = immediate children only)
        excludes: Patterns to exclude
        min_size: Minimum size in bytes to include
        progress_callback: Called with (current, total) for progress updates

    Returns:
        List of SizeEntry objects sorted by size descending
    """
    directory = Path(directory).resolve()
    if not directory.is_dir():
        raise NotADirectoryError(f"Not a directory: {directory}")

    excludes = excludes or []
    entries: list[SizeEntry] = []

    # Collect directories at specified depth
    dirs_to_measure: list[Path] = []

    def collect_dirs(path: Path, current_depth: int):
        if current_depth > depth:
            return

        try:
            for item in path.iterdir():
                if item.is_dir() and not should_exclude(item, excludes):
                    dirs_to_measure.append(item)
                    if current_depth < depth:
                        collect_dirs(item, current_depth + 1)
        except PermissionError:
            pass

    # Always include the root directory
    dirs_to_measure.append(directory)
    collect_dirs(directory, 1)

    total_dirs = len(dirs_to_measure)

    for i, dir_path in enumerate(dirs_to_measure):
        size = get_dir_size(dir_path, excludes)

        if min_size is not None and size < min_size:
            if progress_callback:
                progress_callback(i + 1, total_dirs)
            continue

        entries.append(SizeEntry(path=str(dir_path), size_bytes=size))

        if progress_callback:
            progress_callback(i + 1, total_dirs)

    # Sort by size descending
    entries.sort(key=lambda e: e.size_bytes, reverse=True)

    # Apply limit
    if limit > 0:
        entries = entries[:limit]

    return entries


def format_output(
    entries: list[SizeEntry],
    as_json: bool = False,
) -> str:
    """Format entries for plain text display.

    Args:
        entries: List of SizeEntry objects
        as_json: Output as JSON

    Returns:
        Formatted string
    """
    if as_json:
        return json.dumps([e.to_dict() for e in entries], indent=2)

    if not entries:
        return "No results found."

    lines = []
    # Find max size width for alignment
    max_size_len = max(len(e.size_human) for e in entries)

    for entry in entries:
        size_display = entry.size_human.rjust(max_size_len)
        lines.append(f"{size_display}\t{entry.path}")

    return "\n".join(lines)
