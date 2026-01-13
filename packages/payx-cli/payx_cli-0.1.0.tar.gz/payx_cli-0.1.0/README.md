# payx-cli

A CLI tool to automate engineer onboarding tasks: processor setup, test transactions, merchant migration, and environment configuration management.

## Features

- Interactive CLI driven by `typer`
- Streamline processor and merchant setup
- Run test transactions for verification
- Migrate merchant configurations between environments
- Manage and validate environment configuration files

## Requirements

- Python >= 3.13
- See `pyproject.toml` for pinned dependencies (uses `typer >=0.21.0,<0.22.0`)

## Installation

Clone the repository and install with your preferred tool:

```bash
git clone https://github.com/rakibulhaq/payx-cli.git
cd payx-cli
python -m venv .venv
source .venv/bin/activate
pip install -e .
```
