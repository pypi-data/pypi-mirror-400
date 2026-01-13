# DateId

| **Category** | **Status' and Links**                                                                                                                                                                         |
| ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| General      | [![][general_maintenance_y_img]][general_maintenance_y_lnk] [![][general_semver_pic]][general_semver_link] [![][general_license_img]][general_license_lnk]                                    |
| CD/CI        | [![][gh_tests_img]][gh_tests_lnk] [![][cicd_codestyle_img]][cicd_codestyle_lnk] [![][cicd_pre_commit_img]][cicd_pre_commit_lnk] [![][codecov_img]][codecov_lnk] [![][gh_doc_img]][gh_doc_lnk] |
| PyPI         | [![][pypi_release_img]][pypi_release_lnk] [![][pypi_py_versions_img]][pypi_py_versions_lnk] [![][pypi_format_img]][pypi_format_lnk] [![][pypi_downloads_img]][pypi_downloads_lnk]             |
| Github       | [![][gh_issues_img]][gh_issues_lnk] [![][gh_language_img]][gh_language_lnk] [![][gh_last_commit_img]][gh_last_commit_lnk] [![][gh_deployment_img]][gh_deployment_lnk]                         |

# Overview

`DateId` is a Python utility designed to calculate unique integer identifiers for dates and months relative to a configurable base date. This is particularly useful for database indexing, time-series analysis, or any application where a continuous integer representation of time is more efficient than standard date formats.

## Key Features

- **Day ID Calculation**: Compute a unique integer for any given date.
- **Month ID Calculation**: Compute a unique integer for any given month.
- **Flexible Base Date**: Set a custom base date (defaults to 2008-01-01).
- **Range Generation**: Generate sequences of day and month IDs for a specified period.
- **Date Conversion**: Convert a `DayID` back into a standard date object or string.
- **Leap Year Support**: Built-in utility for leap year verification.

## Basic Usage

### Initializing DateId

```python
from dateid import DateId

# Initialize with default base date (2008-01-01)
di = DateId()

# Initialize with a custom base date
di_custom = DateId(p_base_date_str="2000-01-01")
```

### Calculating IDs

```python
# Get Day ID for a specific date
day_id = di.calc_day_id(p_target_date_str="2023-12-25")

# Get Month ID for a specific date
month_id = di.calc_month_id(p_target_date_str="2023-12-25")
```

### Converting ID back to Date

```python
# Get date for a specific Day ID
di.specific_date(p_day_id=5838)
print(di.target_date_str)  # Output: 20231225
```

### Generating Ranges

```python
# Generate ranges between two dates
days_tbl, months_tbl = di.generate_range("2023-01-01", "2023-01-05")
```

[cicd_codestyle_img]: https://img.shields.io/badge/code%20style-black-000000.svg "Black"
[cicd_codestyle_lnk]: https://github.com/psf/black "Black"
[cicd_pre_commit_img]: https://img.shields.io/github/actions/workflow/status/BrightEdgeeServices/DateId/pre-commit.yml?label=pre-commit "Pre-Commit"
[cicd_pre_commit_lnk]: https://github.com/BrightEdgeeServices/DateId/blob/master/.github/workflows/pre-commit.yml "Pre-Commit"
[codecov_img]: https://img.shields.io/codecov/c/gh/BrightEdgeeServices/DateId "CodeCov"
[codecov_lnk]: https://app.codecov.io/gh/BrightEdgeeServices/DateId "CodeCov"
[general_license_img]: https://img.shields.io/pypi/l/DateId "License"
[general_license_lnk]: https://github.com/BrightEdgeeServices/DateId/blob/master/LICENSE "License"
[general_maintenance_y_img]: https://img.shields.io/badge/Maintenance%20Intended-%E2%9C%94-green.svg?style=flat-square "Maintenance - intended"
[general_maintenance_y_lnk]: http://unmaintained.tech/ "Maintenance - intended"
[general_semver_link]: https://semver.org/ "Sentic Versioning - 2.0.0"
[general_semver_pic]: https://img.shields.io/badge/Semantic%20Versioning-2.0.0-brightgreen.svg?style=flat-square "Sentic Versioning - 2.0.0"
[gh_deployment_img]: https://img.shields.io/github/deployments/BrightEdgeeServices/DateId/pypi "GitHub - PiPy Deployment"
[gh_deployment_lnk]: https://github.com/BrightEdgeeServices/DateId/deployments/pypi "GitHub - PiPy Deployment"
[gh_doc_img]: https://img.shields.io/readthedocs/DateId "Read the Docs"
[gh_doc_lnk]: https://github.com/BrightEdgeeServices/DateId/blob/master/.github/workflows/check-rst-documentation.yml "Read the Docs"
[gh_issues_img]: https://img.shields.io/github/issues-raw/BrightEdgeeServices/DateId "GitHub - Issue Counter"
[gh_issues_lnk]: https://github.com/BrightEdgeeServices/DateId/issues "GitHub - Issue Counter"
[gh_language_img]: https://img.shields.io/github/languages/top/BrightEdgeeServices/DateId "GitHub - Top Language"
[gh_language_lnk]: https://github.com/BrightEdgeeServices/DateId "GitHub - Top Language"
[gh_last_commit_img]: https://img.shields.io/github/last-commit/BrightEdgeeServices/DateId/master "GitHub - Last Commit"
[gh_last_commit_lnk]: https://github.com/BrightEdgeeServices/DateId/commit/master "GitHub - Last Commit"
[gh_tests_img]: https://img.shields.io/github/actions/workflow/status/BrightEdgeeServices/DateId/ci.yml?label=ci "Test status"
[gh_tests_lnk]: https://github.com/BrightEdgeeServices/DateId/blob/master/.github/workflows/ci.yml "Test status"
[pypi_downloads_img]: https://img.shields.io/pypi/dm/DateId "Monthly downloads"
[pypi_downloads_lnk]: https://pypi.org/project/DateId/ "Monthly downloads"
[pypi_format_img]: https://img.shields.io/pypi/wheel/DateId "PyPI - Format"
[pypi_format_lnk]: https://pypi.org/project/DateId/ "PyPI - Format"
[pypi_py_versions_img]: https://img.shields.io/pypi/pyversions/DateId "PyPI - Supported Python Versions"
[pypi_py_versions_lnk]: https://pypi.org/project/DateId/ "PyPI - Supported Python Versions"
[pypi_release_img]: https://img.shields.io/pypi/v/DateId "Test status"
[pypi_release_lnk]: https://pypi.org/project/DateId/ "Test status"
