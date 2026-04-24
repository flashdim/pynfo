# Usage Documentation for nfo_manager.py

This document provides detailed instructions on how to use the `pynfo.py` script.

## Overview
The `pynfo.py` script is designed to manage NFO files, which are commonly used for storing metadata about media files. This script allows users to create, edit, and delete NFO files efficiently.

## Getting Started
### Prerequisites
- Python 3.x installed on your machine.
- Required libraries:<br>  Use the following command to install required libraries:
  ```bash
  pip install -r requirements.txt
  ```

### How to Use nfo_manager.py

#### 1. Running the Script
To run the script, use the following command:
```bash
python pynfo.py [options]
```

#### 2. Options
- `-h`, `--help`: Show the help message and exit.
- `-c`, `--create <filename>`: Create a new NFO file with the specified filename.
- `-e`, `--edit <filename>`: Edit an existing NFO file.
- `-d`, `--delete <filename>`: Delete the specified NFO file.

### Examples
#### Creating a new NFO file
```bash
python pynfo.py --create myfile.nfo
```
#### Editing an existing NFO file
```bash
python pynfo.py --edit myfile.nfo
```
#### Deleting an NFO file
```bash
python pynfo.py --delete myfile.nfo
```

## Troubleshooting
- Ensure you have the correct permissions to access and modify NFO files.
- If you encounter any issues, refer to the GitHub repository issues page for help.

## Additional Resources
- [GitHub Repository](https://github.com/flashdim/pynfo)
- [Python Documentation](https://docs.python.org/3/)

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
