"""CLI interface for duhs with rich progress bars."""

from __future__ import annotations

import sys

import click
from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table
from rich.text import Text

from .core import (
    SizeEntry,
    find_large_dirs,
    find_large_files,
    format_output,
    parse_size,
)

# Rich console for output
console = Console()

# Common exclude patterns
COMMON_EXCLUDES = [
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    ".tox",
    ".pytest_cache",
    ".mypy_cache",
    "*.pyc",
    ".DS_Store",
    "*.egg-info",
    "dist",
    "build",
    ".next",
    "target",  # Rust/Java
    ".cargo",
    ".rustup",
]


def parse_size_option(ctx, param, value):
    """Click callback to parse size strings."""
    if value is None:
        return None
    try:
        return parse_size(value)
    except ValueError:
        raise click.BadParameter(f"Invalid size format: {value}")


def get_size_style(size_bytes: int) -> str:
    """Get rich style based on size magnitude."""
    if size_bytes >= 1024**3:  # >= 1GB
        return "bold red"
    elif size_bytes >= 1024**2:  # >= 1MB
        return "yellow"
    elif size_bytes >= 1024:  # >= 1KB
        return "cyan"
    return "green"


def print_results_table(entries: list[SizeEntry], title: str):
    """Print results as a rich table."""
    if not entries:
        console.print("[dim]No results found.[/dim]")
        return

    table = Table(show_header=True, header_style="bold", box=None, padding=(0, 1))
    table.add_column("Size", justify="right", style="bold")
    table.add_column("Path", style="dim")

    for entry in entries:
        style = get_size_style(entry.size_bytes)
        size_text = Text(entry.size_human, style=style)
        table.add_row(size_text, entry.path)

    console.print(table)


def create_progress() -> Progress:
    """Create a rich progress bar."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    )


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option()
def main(ctx):
    """duhs - Find the largest files and directories.

    \b
    Examples:
        duhs files              # Top 10 largest files in current dir
        duhs files -n 20 /var   # Top 20 largest files in /var
        duhs dirs               # Top 10 largest directories
        duhs dirs -d 2          # Go 2 levels deep
        duhs files -x           # Exclude common junk (.git, node_modules, etc.)
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.command("files")
@click.argument("directory", default=".", type=click.Path(exists=True, file_okay=False))
@click.option("-n", "--number", default=10, show_default=True, help="Number of results to show")
@click.option("-a", "--all", "show_all", is_flag=True, help="Show all results (no limit)")
@click.option("-e", "--exclude", multiple=True, help="Exclude pattern (can be repeated)")
@click.option("-x", "--exclude-common", is_flag=True, help="Exclude common junk (.git, node_modules, __pycache__, etc.)")
@click.option("-m", "--min-size", callback=parse_size_option, help="Minimum size (e.g., 1M, 500K, 1G)")
@click.option("-j", "--json", "as_json", is_flag=True, help="Output as JSON")
@click.option("--no-progress", is_flag=True, help="Disable progress bar")
def files_command(directory, number, show_all, exclude, exclude_common, min_size, as_json, no_progress):
    """Find the largest files in a directory.

    \b
    Examples:
        duhs files                    # Top 10 in current directory
        duhs files /var/log           # Top 10 in /var/log
        duhs files -n 5 ~/Downloads   # Top 5 in Downloads
        duhs files -x                 # Exclude .git, node_modules, etc.
        duhs files -m 100M            # Only files >= 100MB
        duhs files -a                 # Show all files (sorted by size)
    """
    _run_files(directory, number, show_all, exclude, exclude_common, min_size, as_json, no_progress)


def _run_files(directory, number, show_all, exclude, exclude_common, min_size, as_json, no_progress):
    """Shared implementation for files command."""
    excludes = list(exclude)
    if exclude_common:
        excludes.extend(COMMON_EXCLUDES)

    limit = 0 if show_all else number
    use_progress = not no_progress and not as_json and sys.stdout.isatty()

    try:
        if use_progress:
            with create_progress() as progress:
                task = progress.add_task("Scanning files...", total=None)

                def update_progress(current: int, total: int):
                    progress.update(task, completed=current, total=total)

                entries = find_large_files(
                    directory=directory,
                    limit=limit,
                    excludes=excludes,
                    min_size=min_size,
                    progress_callback=update_progress,
                )
        else:
            entries = find_large_files(
                directory=directory,
                limit=limit,
                excludes=excludes,
                min_size=min_size,
            )
    except NotADirectoryError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)

    if as_json:
        click.echo(format_output(entries, as_json=True))
    else:
        print_results_table(entries, f"Largest files in {directory}")


@main.command("dirs")
@click.argument("directory", default=".", type=click.Path(exists=True, file_okay=False))
@click.option("-n", "--number", default=10, show_default=True, help="Number of results to show")
@click.option("-a", "--all", "show_all", is_flag=True, help="Show all results (no limit)")
@click.option("-d", "--depth", default=1, show_default=True, help="Directory depth to analyze")
@click.option("-e", "--exclude", multiple=True, help="Exclude pattern (can be repeated)")
@click.option("-x", "--exclude-common", is_flag=True, help="Exclude common junk (.git, node_modules, __pycache__, etc.)")
@click.option("-m", "--min-size", callback=parse_size_option, help="Minimum size (e.g., 1M, 500K, 1G)")
@click.option("-j", "--json", "as_json", is_flag=True, help="Output as JSON")
@click.option("--no-progress", is_flag=True, help="Disable progress bar")
def dirs_command(directory, number, show_all, depth, exclude, exclude_common, min_size, as_json, no_progress):
    """Find the largest directories.

    \b
    Examples:
        duhs dirs                    # Top 10 immediate subdirectories
        duhs dirs /home              # Top 10 in /home
        duhs dirs -d 2               # Go 2 levels deep
        duhs dirs -n 20 -d 3         # Top 20, 3 levels deep
        duhs dirs -x                 # Exclude .git, node_modules, etc.
        duhs dirs -m 1G              # Only directories >= 1GB
    """
    _run_dirs(directory, number, show_all, depth, exclude, exclude_common, min_size, as_json, no_progress)


def _run_dirs(directory, number, show_all, depth, exclude, exclude_common, min_size, as_json, no_progress):
    """Shared implementation for dirs command."""
    excludes = list(exclude)
    if exclude_common:
        excludes.extend(COMMON_EXCLUDES)

    limit = 0 if show_all else number
    use_progress = not no_progress and not as_json and sys.stdout.isatty()

    try:
        if use_progress:
            with create_progress() as progress:
                task = progress.add_task("Calculating sizes...", total=None)

                def update_progress(current: int, total: int):
                    progress.update(task, completed=current, total=total)

                entries = find_large_dirs(
                    directory=directory,
                    limit=limit,
                    depth=depth,
                    excludes=excludes,
                    min_size=min_size,
                    progress_callback=update_progress,
                )
        else:
            entries = find_large_dirs(
                directory=directory,
                limit=limit,
                depth=depth,
                excludes=excludes,
                min_size=min_size,
            )
    except NotADirectoryError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)

    if as_json:
        click.echo(format_output(entries, as_json=True))
    else:
        print_results_table(entries, f"Largest directories in {directory}")


# Standalone entry points for ducks/ducksdir aliases
def files_cmd():
    """Entry point for 'ducks' command."""
    args = sys.argv[1:]

    # Convert old-style positional args to new style
    # ducks 20 /var -> duhs files -n 20 /var
    new_args = []
    positional = []

    i = 0
    while i < len(args):
        arg = args[i]
        if arg.startswith("-"):
            new_args.append(arg)
            if arg in ("-n", "--number", "-e", "--exclude", "-d", "--depth", "-m", "--min-size"):
                if i + 1 < len(args):
                    i += 1
                    new_args.append(args[i])
        else:
            positional.append(arg)
        i += 1

    # Handle positional args like original: ducks [number] [directory]
    if positional:
        first = positional[0]
        if first.isdigit():
            new_args.extend(["-n", first])
            if len(positional) > 1:
                new_args.append(positional[1])
        else:
            new_args.append(first)
            if len(positional) > 1 and positional[1].isdigit():
                new_args.extend(["-n", positional[1]])

    sys.argv = [sys.argv[0]] + new_args
    files_command(standalone_mode=True)


def dirs_cmd():
    """Entry point for 'ducksdir' command."""
    args = sys.argv[1:]

    new_args = []
    positional = []

    i = 0
    while i < len(args):
        arg = args[i]
        if arg.startswith("-"):
            new_args.append(arg)
            if arg in ("-n", "--number", "-e", "--exclude", "-d", "--depth", "-m", "--min-size"):
                if i + 1 < len(args):
                    i += 1
                    new_args.append(args[i])
        else:
            positional.append(arg)
        i += 1

    # Handle positional args like original: ducksdir [number] [directory]
    if positional:
        first = positional[0]
        if first.isdigit():
            new_args.extend(["-n", first])
            if len(positional) > 1:
                new_args.append(positional[1])
        else:
            new_args.append(first)
            if len(positional) > 1 and positional[1].isdigit():
                new_args.extend(["-n", positional[1]])

    sys.argv = [sys.argv[0]] + new_args
    dirs_command(standalone_mode=True)


if __name__ == "__main__":
    main()
