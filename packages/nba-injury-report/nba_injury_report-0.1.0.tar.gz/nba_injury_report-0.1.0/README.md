# NBA Injury Report

> Fetch and parse official NBA injury reports from the NBA's public API

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL%203.0-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

## Features

- Fetch injury reports directly from NBA's official source
- Pre-game reports from 2021-22 season onwards
- Export to multiple formats: JSON, CSV, pandas DataFrame, formatted tables

## Installation

```bash
pip install nba-injury-report
```

For pandas DataFrame and table support:
```bash
pip install nba-injury-report[pandas,tabulate]
```

## Quick Start

### As a Library

```python
from nba_injury_report import get_injury_report

# Fetch the injury report
report = get_injury_report("2023-12-18T08:30:00")

# Export to different formats
json_data = report.to_json(indent=2)
csv_data = report.to_csv()
list_data = report.to_list()
df = report.to_dataframe()  # requires pandas
table = report.to_table()  # requires tabulate
```

### Sample Output
```json
[
  {
    "Game Date": "12/18/2023",
    "Game Time": "09:00 (ET)",
    "Matchup": "DAL@DEN",
    "Team": "Dallas Mavericks",
    "Player Name": "Lively II, Dereck",
    "Current Status": "Out",
    "Reason": "Injury/Illness - Left Ankle; Sprain"
  },
  {
    "Game Date": "12/18/2023",
    "Game Time": "09:00 (ET)",
    "Matchup": "DAL@DEN",
    "Team": "Denver Nuggets",
    "Player Name": "Gordon, Aaron",
    "Current Status": "Probable",
    "Reason": "Injury/Illness - Right Heel; Strain"
  }
]
```