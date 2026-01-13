# beetools

| **Category** | **Status' and Links**                                                                                                                                                             |
| ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| General      | [![][general_maintenance_y_img]][general_maintenance_y_lnk] [![][general_semver_pic]][general_semver_link] [![][general_license_img]][general_license_lnk]                        |
| CD/CI        | [![][cicd_codestyle_img]][cicd_codestyle_lnk] [![][codecov_img]][codecov_lnk]                                                                                                     |
| PyPI         | [![][pypi_release_img]][pypi_release_lnk] [![][pypi_py_versions_img]][pypi_py_versions_lnk] [![][pypi_format_img]][pypi_format_lnk] [![][pypi_downloads_img]][pypi_downloads_lnk] |
| Github       | [![][gh_issues_img]][gh_issues_lnk] [![][gh_language_img]][gh_language_lnk] [![][gh_last_commit_img]][gh_last_commit_lnk]                                                         |

`beetools` is a collection of Python utilities designed for the Bright Edge eServices ecosystem. It provides a set of tools for terminal messaging, batch script execution, virtual environment management, and various general-purpose utility functions.

## Key Features

- **Messaging (`beetools.msg`)**: Simplified, colored terminal output for consistent feedback (info, success, warning, error, etc.).
- **Scripting (`beetools.script`)**: Tools for executing batch commands, PowerShell scripts, and managing shell sessions.
- **Virtual Environments (`beetools.venv`)**: Automated setup, activation, and package installation within Python virtual environments.
- **Utilities (`beetools.utils`)**: A broad range of helper functions for OS-specific tasks, directory management, and more.

## Installation

You can install `beetools` via `pip`:

```bash
pip install beetools
```

Or using `poetry`:

```bash
poetry add beetools
```

## Quick Start

### Messaging

```python
from beetools import msg

print(msg.ok("Operation completed successfully!"))
print(msg.error("An error occurred."))
```

### Virtual Environments

```python
from beetools import venv

# Set up a new virtual environment
venv.set_up("path/to/venv", "my_env", package_list=["requests", "pandas"])
```

### Scripting

```python
from beetools import script

# Execute a simple command
script.exec_cmd("dir")
```

[cicd_codestyle_img]: https://img.shields.io/badge/code%20style-black-000000.svg "Black"
[cicd_codestyle_lnk]: https://github.com/psf/black "Black"
[codecov_img]: https://img.shields.io/codecov/c/gh/BrightEdgeeServices/beetools "CodeCov"
[codecov_lnk]: https://app.codecov.io/gh/BrightEdgeeServices/beetools "CodeCov"
[general_license_img]: https://img.shields.io/pypi/l/beetools "License"
[general_license_lnk]: https://github.com/BrightEdgeeServices/beetools/blob/master/LICENSE "License"
[general_maintenance_y_img]: https://img.shields.io/badge/Maintenance%20Intended-%E2%9C%94-green.svg?style=flat-square "Maintenance - intended"
[general_maintenance_y_lnk]: http://unmaintained.tech/ "Maintenance - intended"
[general_semver_link]: https://semver.org/ "Sentic Versioning - 2.0.0"
[general_semver_pic]: https://img.shields.io/badge/Semantic%20Versioning-2.0.0-brightgreen.svg?style=flat-square "Sentic Versioning - 2.0.0"
[gh_issues_img]: https://img.shields.io/github/issues-raw/BrightEdgeeServices/beetools "GitHub - Issue Counter"
[gh_issues_lnk]: https://github.com/BrightEdgeeServices/beetools/issues "GitHub - Issue Counter"
[gh_language_img]: https://img.shields.io/github/languages/top/BrightEdgeeServices/beetools "GitHub - Top Language"
[gh_language_lnk]: https://github.com/BrightEdgeeServices/beetools "GitHub - Top Language"
[gh_last_commit_img]: https://img.shields.io/github/last-commit/BrightEdgeeServices/beetools/master "GitHub - Last Commit"
[gh_last_commit_lnk]: https://github.com/BrightEdgeeServices/beetools/commit/master "GitHub - Last Commit"
[pypi_downloads_img]: https://img.shields.io/pypi/dm/beetools "Monthly downloads"
[pypi_downloads_lnk]: https://pypi.org/project/beetools/ "Monthly downloads"
[pypi_format_img]: https://img.shields.io/pypi/wheel/beetools "PyPI - Format"
[pypi_format_lnk]: https://pypi.org/project/beetools/ "PyPI - Format"
[pypi_py_versions_img]: https://img.shields.io/pypi/pyversions/beetools "PyPI - Supported Python Versions"
[pypi_py_versions_lnk]: https://pypi.org/project/beetools/ "PyPI - Supported Python Versions"
[pypi_release_img]: https://img.shields.io/pypi/v/beetools "Test status"
[pypi_release_lnk]: https://pypi.org/project/beetools/ "Test status"
