# envcheck

A lightweight CLI tool to check your Python environment and validate dependencies from `requirements.txt`.

## Features

- 🐍 Display Python version
- 💻 Show operating system information
- 📦 Validate all dependencies from `requirements.txt`
- ✅ Check if each package is installed with the correct version

## Installation

```bash
pip install pyenvcheckr
```

## Usage

Basic usage (checks `requirements.txt` in current directory):

```bash
pyenvcheckr
```

Specify a custom requirements file:

```bash
pyenvcheckr -r path/to/requirements.txt
```

Show version:

```bash
pyenvcheckr --version
```

## Example Output

```
🔍 Environment Check
------------------------------
🐍 Python Version:
  3.10.8

💻 Operating System:
  Windows 10

📦 Dependencies:
  ✅ requests (2.31.0)
  ✅ numpy (1.26.0)
  ❌ unknown-package (NOT INSTALLED)
```

## Requirements

- Python 3.8 or higher

## License

MIT License - see LICENSE file for details
