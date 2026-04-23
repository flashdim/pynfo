# pynfo

A Python utility to validate and manage NFO metadata files, extracting tag information from file names and ensuring consistency in NFO file contents.

## Overview

**pynfo** helps you organize and maintain NFO files (commonly used for Jellyfin and other media center metadata) by:

- Extracting platform, year, and region information from file names
- Validating that NFO files contain the correct corresponding XML elements
- Automatically fixing missing or incorrect tags
- Providing detailed reporting on file processing

## Features

- **Platform Detection**: Recognize gaming platform tags (NES, SNES, N64, Switch, PlayStation, Xbox, etc.)
- **Year Extraction**: Extract release year from file names in `(YYYY)` format
- **Region Identification**: Detect region codes (U, UK, A, NZ, E, K, J)
- **Studio Management**: Extract studio/developer information from `by <company>` patterns
- **Batch Processing**: Process entire folders of NFO files at once
- **Dry-Run Mode**: Validate files without making changes (read-only by default)
- **Auto-Fix**: Optionally repair missing tags automatically

## Prerequisites

- Python 3.x
- No external dependencies required (uses only Python standard library)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/flashdim/pynfo.git
cd pynfo
```

2. (Optional) Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

## Usage

Basic syntax:
```bash
python nfo_manager.py [OPTIONS] <folder>
```

### Options

- `-t, --tag <TAG>`: Specify a tag to validate (e.g., `(SNES)`, `(2022)`, `(U)`) or use `studio` to check studio tags
- `--fix`: Enable auto-fix mode (modifies NFO files). Without this flag, the script runs in read-only mode
- `folder`: Path to the folder containing .nfo files

### Examples

**Check for studio tags (read-only):**
```bash
python nfo_manager.py /path/to/nfo_files
```

**Validate a specific platform tag:**
```bash
python nfo_manager.py --tag "(SNES)" /path/to/nfo_files
```

**Validate and auto-fix missing year tags:**
```bash
python nfo_manager.py --tag "(2023)" --fix /path/to/nfo_files
```

**Validate region codes and auto-fix:**
```bash
python nfo_manager.py --tag "(J)" --fix /path/to/nfo_files
```

## Supported Tags

### Platform Tags
NES, SNES, N64, Nintendo Switch, Switch 2, Game Boy, Game Boy Color, Game Boy Advance, DS, 3DS, Genesis, Saturn, Dreamcast, PlayStation, PS2, PS3, PS4, PS5, PSP, Vita, Xbox, Xbox 360, Xbox One, Xbox Series X|S, PC, Jaguar, NeoGeo, Arcade, 3DO

### Year Tags
Any year in `(YYYY)` format (e.g., `(2022)`, `(1985)`)

### Region Tags
- `(U)` - United States
- `(UK)` - United Kingdom
- `(A)` - Australia
- `(NZ)` - New Zealand
- `(E)` - Europe
- `(K)` - South Korea
- `(J)` - Japan

## File Naming Convention

For studio detection, use the following file name pattern:
```
Game Title by Developer Name - Other Info.nfo
```

Example: `The Legend of Zelda by Nintendo - (SNES) (1992) (U).nfo`

## For More Information

See [USAGE.md](USAGE.md) for detailed usage documentation.

## License

MIT License - see the [LICENSE](LICENSE) file for details.