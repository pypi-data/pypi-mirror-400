# duhs

Find the largest files and directories. A cross-platform CLI tool with progress bars and color-coded output.

## Installation

```bash
pip install duhs
```

Or install from source:

```bash
git clone https://github.com/beantownbytes/duhs.git
cd duhs
pip install .
```

## Usage

```bash
# Find largest files in current directory
duhs files

# Find largest directories
duhs dirs

# Top 20 largest files in /var
duhs files -n 20 /var

# Directories 2 levels deep
duhs dirs -d 2

# Exclude common junk (.git, node_modules, __pycache__, etc.)
duhs files -x

# Only show files >= 100MB
duhs files -m 100M

# JSON output for scripting
duhs files --json
```

## Commands

### `duhs files [DIRECTORY]`

Find the largest files in a directory.

| Option | Description |
|--------|-------------|
| `-n, --number N` | Number of results (default: 10) |
| `-a, --all` | Show all results |
| `-e, --exclude PAT` | Exclude pattern (repeatable) |
| `-x, --exclude-common` | Exclude .git, node_modules, __pycache__, etc. |
| `-m, --min-size SIZE` | Minimum size (e.g., 1M, 500K, 1G) |
| `-j, --json` | Output as JSON |
| `--no-progress` | Disable progress bar |

### `duhs dirs [DIRECTORY]`

Find the largest directories.

| Option | Description |
|--------|-------------|
| `-n, --number N` | Number of results (default: 10) |
| `-a, --all` | Show all results |
| `-d, --depth N` | Directory depth (default: 1) |
| `-e, --exclude PAT` | Exclude pattern (repeatable) |
| `-x, --exclude-common` | Exclude .git, node_modules, __pycache__, etc. |
| `-m, --min-size SIZE` | Minimum size (e.g., 1M, 500K, 1G) |
| `-j, --json` | Output as JSON |
| `--no-progress` | Disable progress bar |

## Features

- Progress bar with real-time file count
- Color-coded output (GB=red, MB=yellow, KB=cyan)
- Accurate disk usage (not apparent size) on macOS/Linux
- Cross-platform (macOS, Linux, Windows)
- JSON output for scripting

## License

MIT
