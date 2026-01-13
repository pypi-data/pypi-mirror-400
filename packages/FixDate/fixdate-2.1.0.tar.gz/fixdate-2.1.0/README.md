# FixDateIt

| **Category** | **Status' and Links**                                                                                                                                                                         |
| ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| General      | [![][general_maintenance_y_img]][general_maintenance_y_lnk] [![][general_semver_pic]][general_semver_link] [![][general_license_img]][general_license_lnk]                                    |
| CD/CI        | [![][gh_tests_img]][gh_tests_lnk] [![][cicd_codestyle_img]][cicd_codestyle_lnk] [![][cicd_pre_commit_img]][cicd_pre_commit_lnk] [![][codecov_img]][codecov_lnk] [![][gh_doc_img]][gh_doc_lnk] |
| PyPI         | [![][pypi_release_img]][pypi_release_lnk] [![][pypi_py_versions_img]][pypi_py_versions_lnk] [![][pypi_format_img]][pypi_format_lnk] [![][pypi_downloads_img]][pypi_downloads_lnk]             |
| Github       | [![][gh_issues_img]][gh_issues_lnk] [![][gh_language_img]][gh_language_lnk] [![][gh_last_commit_img]][gh_last_commit_lnk] [![][gh_deployment_img]][gh_deployment_lnk]                         |

# Overview

`FixDateIt` is a Python library designed to intelligently correct and normalize date strings into a standard format. It handles various common date formats, separators, and even attempts to fix common data entry errors.

### Key Features

- **Format Normalization:** Converts various input date formats (e.g., YMD, DMY) into a consistent output format (defaulting to `%Y%m%d`).
- **Flexible Separators:** Automatically handles different separators like `/`, `-`, and `.`.
- **Heuristic Corrections:**
  - **Century Guessing:** Automatically adds the correct century (1900s or 2000s) for two-digit years.
  - **Day/Month Swapping:** Detects and fixes cases where day and month might have been swapped (e.g., if month > 12).
  - **Out-of-range Day Correction:** Can optionally cap days to the maximum valid day for a given month (e.g., setting Feb 30th to Feb 28th/29th).
- **Numeric String Parsing:** Handles compact numeric strings (e.g., "20230101" or "010123") by intelligently inserting separators before parsing.
- **Month Name Support:** Recognizes three-letter month abbreviations (e.g., "JAN", "FEB").

### Basic Usage

```python
from fixdate import FixDate

# Basic conversion
fd = FixDate("01-15-2023", p_in_format="MDY")
print(fd.date_str)  # Output: 20230115

# Fixing swapped day/month
fd = FixDate("31/12/2023", p_in_format="MDY")
print(fd.date_str)  # Output: 20231231

# Handling abbreviations
fd = FixDate("15-JAN-23", p_in_format="DMY")
print(fd.date_str)  # Output: 20230115
```

______________________________________________________________________

[cicd_codestyle_img]: https://img.shields.io/badge/code%20style-black-000000.svg "Black"
[cicd_codestyle_lnk]: https://github.com/psf/black "Black"
[cicd_pre_commit_img]: https://img.shields.io/github/actions/workflow/status/BrightEdgeeServices/FixDate/pre-commit.yml?label=pre-commit "Pre-Commit"
[cicd_pre_commit_lnk]: https://github.com/BrightEdgeeServices/FixDate/blob/master/.github/workflows/pre-commit.yml "Pre-Commit"
[codecov_img]: https://img.shields.io/codecov/c/gh/BrightEdgeeServices/FixDate "CodeCov"
[codecov_lnk]: https://app.codecov.io/gh/BrightEdgeeServices/FixDate "CodeCov"
[general_license_img]: https://img.shields.io/pypi/l/FixDateIt "License"
[general_license_lnk]: https://github.com/BrightEdgeeServices/FixDate/blob/master/LICENSE "License"
[general_maintenance_y_img]: https://img.shields.io/badge/Maintenance%20Intended-%E2%9C%94-green.svg?style=flat-square "Maintenance - intended"
[general_maintenance_y_lnk]: http://unmaintained.tech/ "Maintenance - intended"
[general_semver_link]: https://semver.org/ "Sentic Versioning - 2.0.0"
[general_semver_pic]: https://img.shields.io/badge/Semantic%20Versioning-2.0.0-brightgreen.svg?style=flat-square "Sentic Versioning - 2.0.0"
[gh_deployment_img]: https://img.shields.io/github/deployments/BrightEdgeeServices/FixDate/pypi "GitHub - PiPy Deployment"
[gh_deployment_lnk]: https://github.com/BrightEdgeeServices/FixDate/deployments/pypi "GitHub - PiPy Deployment"
[gh_doc_img]: https://img.shields.io/readthedocs/FixDateIt "Read the Docs"
[gh_doc_lnk]: https://github.com/BrightEdgeeServices/FixDate/blob/master/.github/workflows/check-rst-documentation.yml "Read the Docs"
[gh_issues_img]: https://img.shields.io/github/issues-raw/BrightEdgeeServices/FixDate "GitHub - Issue Counter"
[gh_issues_lnk]: https://github.com/BrightEdgeeServices/FixDate/issues "GitHub - Issue Counter"
[gh_language_img]: https://img.shields.io/github/languages/top/BrightEdgeeServices/FixDate "GitHub - Top Language"
[gh_language_lnk]: https://github.com/BrightEdgeeServices/FixDate "GitHub - Top Language"
[gh_last_commit_img]: https://img.shields.io/github/last-commit/BrightEdgeeServices/FixDate/master "GitHub - Last Commit"
[gh_last_commit_lnk]: https://github.com/BrightEdgeeServices/FixDate/commit/master "GitHub - Last Commit"
[gh_tests_img]: https://img.shields.io/github/actions/workflow/status/BrightEdgeeServices/FixDate/ci.yml?label=ci "Test status"
[gh_tests_lnk]: https://github.com/BrightEdgeeServices/FixDate/blob/master/.github/workflows/ci.yml "Test status"
[pypi_downloads_img]: https://img.shields.io/pypi/dm/FixDateIt "Monthly downloads"
[pypi_downloads_lnk]: https://pypi.org/project/FixDateIt/ "Monthly downloads"
[pypi_format_img]: https://img.shields.io/pypi/wheel/FixDateIt "PyPI - Format"
[pypi_format_lnk]: https://pypi.org/project/FixDateIt/ "PyPI - Format"
[pypi_py_versions_img]: https://img.shields.io/pypi/pyversions/FixDateIt "PyPI - Supported Python Versions"
[pypi_py_versions_lnk]: https://pypi.org/project/FixDateIt/ "PyPI - Supported Python Versions"
[pypi_release_img]: https://img.shields.io/pypi/v/FixDateIt "Test status"
[pypi_release_lnk]: https://pypi.org/project/FixDateIt/ "Test status"
