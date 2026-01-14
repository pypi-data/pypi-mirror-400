# Data Validation Tool (dvt)

CLI tool for dbt data validation workflows. Born from the scripts folder of [dbt-audit-helper-ext](https://github.com/infinitelambda/dbt-audit-helper-ext), this tool consolidates validation utilities into a proper Python package.

## Table of Contents

- [Data Validation Tool (dvt)](#data-validation-tool-dvt)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Quick Start](#quick-start)
  - [Commands](#commands)
    - [dvt init](#dvt-init)
    - [dvt run](#dvt-run)
    - [dvt cloud](#dvt-cloud)
  - [Development](#development)
  - [License](#license)

## Installation

```bash
pip install data-validation-tool
```

Or with uv:

```bash
uv pip install data-validation-tool
```

## Quick Start

```bash
# Generate validation macros for your dbt models
dvt init --models-dir models/03_mart

# Run validations
dvt run --models-dir models/03_mart --type all

# Generate dbt Cloud job configurations
export DBT_CLOUD_ACCOUNT_ID=12345
export DBT_CLOUD_PROJECT_ID=67890
export DBT_CLOUD_ENVIRONMENT_ID=11111
dvt cloud --models-dir models/03_mart
```

## Commands

### dvt init

Generate validation macros for dbt models. Scans your models directory and creates validation macro files compatible with dbt-audit-helper-ext.

```bash
dvt init [OPTIONS]

Options:
  -d, --models-dir PATH   Directory containing dbt models (default: models/03_mart)
  -m, --model TEXT        Specific model name to generate macros for
  -o, --output-dir PATH   Output directory for generated macros (default: macros/validation)
  --help                  Show this message and exit
```

### dvt run

Execute validation processes. Runs dbt models and executes validation macros to compare source and target data.

```bash
dvt run [OPTIONS]

Options:
  -d, --models-dir PATH   Directory containing dbt models (default: models/03_mart)
  -m, --model TEXT        Specific model name to validate
  -t, --type TYPE         Validation type: all, count, schema, all_row, all_col (default: all)
  -p, --audit-date TEXT   Audit helper date for cloning from legacy data
  -r, --skip-run          Skip model runs, validate only
  -v, --run-only          Run models only, skip validation
  --help                  Show this message and exit
```

### dvt cloud

Generate dbt Cloud job configurations as YAML. Creates files compatible with [dbt-jobs-as-code](https://github.com/dbt-labs/dbt-jobs-as-code).

```bash
dvt cloud [OPTIONS]

Options:
  -d, --models-dir PATH      Directory containing dbt models (default: models/03_mart)
  -m, --model TEXT           Specific model name to create job for
  -o, --output PATH          Output path for jobs YAML (default: dataops/dbt_cloud_jobs.yml)
  --account-id TEXT          dbt Cloud account ID (or set DBT_CLOUD_ACCOUNT_ID) [required]
  --project-id TEXT          dbt Cloud project ID (or set DBT_CLOUD_PROJECT_ID) [required]
  --environment-id TEXT      dbt Cloud environment ID (or set DBT_CLOUD_ENVIRONMENT_ID) [required]
  --help                     Show this message and exit
```

## Development

Clone the repository and install development dependencies:

```bash
git clone https://github.com/infinitelambda/data-validation-tool.git
cd data-validation-tool
uv sync --all-extras
```

Run tests with coverage:

```bash
uv run pytest
```

Format and lint code:

```bash
uv run ruff format .
uv run ruff check .
```

## License

Apache License 2.0 - see [LICENSE](LICENSE) for details.
