# Contributor Checker

This tool helps to generate a report on commit contributors for a specific Git branch. It fetches commit details, filters contributors by email domain, and generates a detailed report with pie charts.

## Features:
- Generate a report on contributors' commits.
- Segregate contributors based on their domain.
- Generate pie charts to visualize domain vs non-domain contributors.
- Show commit details like SHA, message, name, and email.

## Installation:
To run the script, first install the necessary Python dependencies.

### 1. Clone this repository (if applicable):
```bash
git clone https://github.com/SelamHemanth/infobellit-backport-tools.git
cd infobellit-backport-tools
git checkout contributor-checker
```

### 2. Install the package:
```bash
./installer
```

## Usage:
### Basic Command:
To generate the report for a specific branch and domain, use the following command:

```bash
contributor-checker -b=<branch_name> -d=<domain_name>
#Ex: contributor-checker -b=master -d=amd.com
```

### Options:
* `-b/--branch:` The Git branch name.
* `-d/--domain:` The domain to filter contributors by email.
* `-v/--version:` Show version and author details.
* `-h/--help`: Show details about tool.

### Output:
The script generates an HTML file contributor-report.html containing:
* A summary table of contributors.
* Two pie charts showing the contribution distribution.
* A detailed commit report.

## Author:
* `Name:` Hemanth Selam
* `Email:` Hemanth.Selam@gamil.com
* `Version:` 20241219
