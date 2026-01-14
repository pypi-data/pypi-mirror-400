# DataCheck

**Lightweight data quality validation CLI tool with enterprise features**

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

DataCheck is a fast, CLI-first data validation tool for data engineers who need to validate data quality without heavy frameworks.

## Quick Start

```bash
# Install
pip install datacheck-cli

# Create validation rules (validation.yaml)
checks:
  - name: age_validation
    column: age
    rules:
      not_null: true
      min: 18
      max: 120

# Validate your data
datacheck validate data.csv --config validation.yaml
```

## Key Features

### Core Validation
- **Multiple formats**: CSV, Parquet, PostgreSQL, MySQL, SQL Server
- **Simple YAML config**: Easy to write and version control
- **Rich terminal output**: Beautiful, colorful validation results
- **CI/CD ready**: Proper exit codes (0=pass, 1=fail, 2+=errors)

### Enterprise Features (v0.2.0)
- **Database connectors**: Direct validation of PostgreSQL, MySQL, SQL Server tables
- **Custom plugins**: Write validation rules in Python, load dynamically
- **Row sampling**: Random, stratified, top-N sampling for large datasets
- **Parallel execution**: Multi-core processing for datasets with 10,000+ rows
- **Data profiling**: Comprehensive quality analysis with `datacheck profile`
- **Slack notifications**: Real-time validation results to Slack webhooks

### Validation Rules
- `not_null`: No missing values
- `min` / `max`: Numeric range validation
- `unique`: Detect duplicates
- `regex`: Pattern matching
- `allowed_values`: Whitelist validation

## Installation

```bash
# Basic installation
pip install datacheck-cli

# Install all features (recommended)
pip install datacheck-cli[all]

# Individual features
pip install datacheck-cli[postgresql]  # PostgreSQL
pip install datacheck-cli[mysql]       # MySQL
pip install datacheck-cli[mssql]       # SQL Server
```

**`[all]` includes**: PostgreSQL, MySQL, SQL Server, DuckDB (Linux/macOS), and all enterprise features.

## Usage Examples

### File Validation
```bash
# Basic validation
datacheck validate data.csv --config rules.yaml

# JSON output
datacheck validate data.csv --format json --output results.json

# Parallel execution for large files
datacheck validate large_data.csv --parallel --workers 4
```

### Database Validation
```bash
# PostgreSQL
datacheck validate "postgresql://user:pass@localhost/db" --table users

# MySQL with WHERE clause
datacheck validate "mysql://user:pass@localhost/db" --table orders \
  --where "created_at > '2024-01-01'"

# Custom SQL query
datacheck validate "postgresql://localhost/db" \
  --query "SELECT * FROM users WHERE active = true"
```

### Data Profiling
```bash
# Terminal output
datacheck profile data.csv

# JSON export
datacheck profile data.csv --output profile.json
```

### Row Sampling
```bash
# Random 10% sample
datacheck validate data.csv --sample-rate 0.1

# First 1000 rows
datacheck validate data.csv --top 1000

# Stratified sampling
datacheck validate data.csv --sample-count 5000 --stratify category
```

### Slack Notifications
```bash
datacheck validate data.csv \
  --slack-webhook https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

## Configuration Example

```yaml
# .datacheck.yaml
checks:
  - name: user_id_validation
    column: user_id
    rules:
      not_null: true
      unique: true

  - name: email_format
    column: email
    rules:
      not_null: true
      regex: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"

  - name: age_range
    column: age
    rules:
      min: 18
      max: 120

  - name: status_values
    column: status
    rules:
      allowed_values: ["active", "inactive", "pending"]

# Optional: Custom plugins
plugins:
  - ./custom_rules.py

# Optional: Sampling
sampling:
  strategy: random
  rate: 0.1
  seed: 42
```

## Exit Codes

DataCheck uses standard exit codes for automation:

| Code | Meaning | Description |
|------|---------|-------------|
| `0` | Success | All validation rules passed |
| `1` | Failed | Some validation rules failed |
| `2` | Config Error | Configuration file error |
| `3` | Data Error | Data loading error |
| `4` | Runtime Error | Unexpected error |

## CI/CD Integration

### GitHub Actions
```yaml
- name: Validate Data
  run: |
    pip install datacheck-cli[all]
    datacheck validate data/export.csv --config validation.yaml
```

### GitLab CI
```yaml
validate:
  script:
    - pip install datacheck-cli[all]
    - datacheck validate data.csv --config rules.yaml
```

### Pre-commit Hook
```bash
#!/bin/bash
for file in $(git diff --cached --name-only | grep '\.csv$'); do
  datacheck validate "$file" || exit 1
done
```

## Custom Validation Rules

Create custom rules in Python:

```python
# custom_rules.py
from datacheck.plugins import rule

@rule("custom_email_domain")
def validate_email_domain(df, column, allowed_domains):
    """Validate email addresses are from allowed domains."""
    emails = df[column].dropna()
    domains = emails.str.split('@').str[1]
    invalid = ~domains.isin(allowed_domains)

    if invalid.any():
        failed_indices = df[invalid].index.tolist()
        return False, failed_indices
    return True, []
```

Use in config:
```yaml
plugins:
  - ./custom_rules.py

checks:
  - name: corporate_email
    column: email
    rules:
      custom_email_domain:
        allowed_domains: ["company.com", "corp.com"]
```

## Performance

- **Fast**: Validates 1M rows with 10 rules in ~2-3 seconds
- **Scalable**: Parallel processing for large datasets (10,000+ rows)
- **Efficient**: Uses pandas for optimized data operations

## Requirements

- Python 3.10+
- pandas 2.0+
- typer, rich, pyyaml, pyarrow

Optional:
- psycopg2 (PostgreSQL)
- mysql-connector-python (MySQL)
- pyodbc (SQL Server)

## Links

- **Documentation**: [https://yash-chauhan-dev.github.io/datacheck/](https://yash-chauhan-dev.github.io/datacheck/)
- **Source Code**: [https://github.com/yash-chauhan-dev/datacheck](https://github.com/yash-chauhan-dev/datacheck)
- **Issue Tracker**: [https://github.com/yash-chauhan-dev/datacheck/issues](https://github.com/yash-chauhan-dev/datacheck/issues)

## License

MIT License - see [LICENSE](https://github.com/yash-chauhan-dev/datacheck/blob/main/LICENSE) for details.

---

**Made for data engineers who value simplicity and speed.**
