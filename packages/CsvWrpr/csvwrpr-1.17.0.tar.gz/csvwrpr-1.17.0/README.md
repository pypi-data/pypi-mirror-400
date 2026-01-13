# CsvWrpr

| **Category** | **Status' and Links**                                                                                                                                                                         |
| ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| General      | [![][general_maintenance_y_img]][general_maintenance_y_lnk] [![][general_semver_pic]][general_semver_link] [![][general_license_img]][general_license_lnk]                                    |
| CD/CI        | [![][gh_tests_img]][gh_tests_lnk] [![][cicd_codestyle_img]][cicd_codestyle_lnk] [![][cicd_pre_commit_img]][cicd_pre_commit_lnk] [![][codecov_img]][codecov_lnk] [![][gh_doc_img]][gh_doc_lnk] |
| PyPI         | [![][pypi_release_img]][pypi_release_lnk] [![][pypi_py_versions_img]][pypi_py_versions_lnk] [![][pypi_format_img]][pypi_format_lnk] [![][pypi_downloads_img]][pypi_downloads_lnk]             |
| Github       | [![][gh_issues_img]][gh_issues_lnk] [![][gh_language_img]][gh_language_lnk] [![][gh_last_commit_img]][gh_last_commit_lnk] [![][gh_deployment_img]][gh_deployment_lnk]                         |

Wrapper for csv files.

## Overview

CsvWrpr is a versatile Python utility designed to simplify the process of reading and restructuring CSV data. It provides a convenient wrapper around standard CSV operations, allowing developers to easily convert CSV content into various Python data structures like lists, dictionaries, or tuples.

Beyond simple conversion, CsvWrpr offers robust header manipulation capabilities, including adding, removing, or replacing headers on the fly. It is also equipped to handle different delimiters, filter data subsets, and clean up undesirable characters within the source file.

### Key Features

- **Flexible Data Structures**: Convert CSV data into Lists, Tuples (optimized for database imports), or Dictionaries (with support for nested dimensions).
- **Header Management**: Easily delete existing headers, inject new ones, or replace them entirely during the wrapping process.
- **Smart Delimiter Detection**: Automatically identify or explicitly define data and header delimiters.
- **Data Sanitization**: Handle and correct undesirable characters or formatting inconsistencies within the CSV.
- **Subset Selection**: Extract specific ranges or subsets of data from the original file.
- **Progress Tracking**: Built-in support for progress bars and verbose messaging for large file processing.

[cicd_codestyle_img]: https://img.shields.io/badge/code%20style-black-000000.svg "Black"
[cicd_codestyle_lnk]: https://github.com/psf/black "Black"
[cicd_pre_commit_img]: https://img.shields.io/github/actions/workflow/status/hendrikdutoit/PoetryExample/pre-commit.yml?label=pre-commit "Pre-Commit"
[cicd_pre_commit_lnk]: https://github.com/hendrikdutoit/PoetryExample/blob/master/.github/workflows/pre-commit.yml "Pre-Commit"
[codecov_img]: https://img.shields.io/codecov/c/gh/hendrikdutoit/PoetryExample "CodeCov"
[codecov_lnk]: https://app.codecov.io/gh/hendrikdutoit/PoetryExample "CodeCov"
[general_license_img]: https://img.shields.io/pypi/l/CsvWrpr "License"
[general_license_lnk]: https://github.com/hendrikdutoit/PoetryExample/blob/master/LICENSE "License"
[general_maintenance_y_img]: https://img.shields.io/badge/Maintenance%20Intended-%E2%9C%94-green.svg?style=flat-square "Maintenance - intended"
[general_maintenance_y_lnk]: http://unmaintained.tech/ "Maintenance - intended"
[general_semver_link]: https://semver.org/ "Sentic Versioning - 2.0.0"
[general_semver_pic]: https://img.shields.io/badge/Semantic%20Versioning-2.0.0-brightgreen.svg?style=flat-square "Sentic Versioning - 2.0.0"
[gh_deployment_img]: https://img.shields.io/github/deployments/hendrikdutoit/PoetryExample/pypi "GitHub - PiPy Deployment"
[gh_deployment_lnk]: https://github.com/hendrikdutoit/PoetryExample/deployments/pypi "GitHub - PiPy Deployment"
[gh_doc_img]: https://img.shields.io/readthedocs/CsvWrpr "Read the Docs"
[gh_doc_lnk]: https://github.com/hendrikdutoit/PoetryExample/blob/master/.github/workflows/check-rst-documentation.yml "Read the Docs"
[gh_issues_img]: https://img.shields.io/github/issues-raw/hendrikdutoit/PoetryExample "GitHub - Issue Counter"
[gh_issues_lnk]: https://github.com/hendrikdutoit/PoetryExample/issues "GitHub - Issue Counter"
[gh_language_img]: https://img.shields.io/github/languages/top/hendrikdutoit/PoetryExample "GitHub - Top Language"
[gh_language_lnk]: https://github.com/hendrikdutoit/PoetryExample "GitHub - Top Language"
[gh_last_commit_img]: https://img.shields.io/github/last-commit/hendrikdutoit/PoetryExample/master "GitHub - Last Commit"
[gh_last_commit_lnk]: https://github.com/hendrikdutoit/PoetryExample/commit/master "GitHub - Last Commit"
[gh_tests_img]: https://img.shields.io/github/actions/workflow/status/hendrikdutoit/PoetryExample/ci.yml?label=ci "Test status"
[gh_tests_lnk]: https://github.com/hendrikdutoit/PoetryExample/blob/master/.github/workflows/ci.yml "Test status"
[pypi_downloads_img]: https://img.shields.io/pypi/dm/CsvWrpr "Monthly downloads"
[pypi_downloads_lnk]: https://pypi.org/project/CsvWrpr/ "Monthly downloads"
[pypi_format_img]: https://img.shields.io/pypi/wheel/CsvWrpr "PyPI - Format"
[pypi_format_lnk]: https://pypi.org/project/CsvWrpr/ "PyPI - Format"
[pypi_py_versions_img]: https://img.shields.io/pypi/pyversions/CsvWrpr "PyPI - Supported Python Versions"
[pypi_py_versions_lnk]: https://pypi.org/project/CsvWrpr/ "PyPI - Supported Python Versions"
[pypi_release_img]: https://img.shields.io/pypi/v/CsvWrpr "Test status"
[pypi_release_lnk]: https://pypi.org/project/CsvWrpr/ "Test status"
