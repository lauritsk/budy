# budy

An itsy bitsy CLI budgeting assistant for people who want to track spending, set budgets, and inspect bank data without leaving the terminal.

Budy is local-first: it stores your data in SQLite, imports bank CSV exports, and gives you practical reports like monthly budget status, top payees, weekday spending habits, and outlier detection.

> [!NOTE]
> By default, Budy stores both `config.toml` and `budy.db` in your platform app-data directory. Set `BUDY_DB_URL` if you want to use a different database URL.

## Features

- Import bank statement CSVs into a local SQLite database
- Built-in presets for **LHV**, **SEB**, and **Swedbank**
- Define custom bank import formats in `config.toml`
- Add, update, delete, list, export, and search transactions
- Organize spending with categories and import-time auto-categorization rules
- Set monthly budgets or generate suggestions from historical spending
- Inspect your finances with monthly, yearly, payee, weekday, and volatility reports
- Export transactions as CSV or JSON

## Requirements

- Python **3.14+**
- [`mise`](https://mise.jdx.dev/)

This repository uses `mise` and `uv` for setup and execution.

## Quick start

Clone the repo, install the toolchain, sync dependencies, then run the interactive setup:

```bash
mise install
mise run setup
mise exec uv -- uv run budy setup
```

The setup flow will:

1. ask for your name
2. let you choose a currency symbol
3. write a `config.toml`
4. optionally import your first bank CSV

## Typical workflow

```bash
# Add a category
mise exec uv -- uv run budy categories add Groceries --color green

# Add an auto-categorization rule used during CSV import
mise exec uv -- uv run budy categories rules add spotify --category-id 1

# Import a bank statement
mise exec uv -- uv run budy transactions import --bank lhv --file ./statement.csv

# Generate budget suggestions from historical data
mise exec uv -- uv run budy budgets generate --year 2026 --yes

# View reports
mise exec uv -- uv run budy reports month
mise exec uv -- uv run budy reports payees
mise exec uv -- uv run budy reports volatility
```

## Core commands

| Goal | Command |
| --- | --- |
| Interactive setup | `mise exec uv -- uv run budy setup` |
| Add a transaction | `mise exec uv -- uv run budy transactions add --amount 12.50` |
| List recent transactions | `mise exec uv -- uv run budy transactions list` |
| Import a CSV statement | `mise exec uv -- uv run budy transactions import --bank lhv --file ./statement.csv` |
| Export transactions | `mise exec uv -- uv run budy transactions export --output ./transactions.csv --format csv` |
| Add a monthly budget | `mise exec uv -- uv run budy budgets add --amount 500 --month 4 --year 2026` |
| Generate budgets automatically | `mise exec uv -- uv run budy budgets generate --year 2026 --yes` |
| Show monthly budget status | `mise exec uv -- uv run budy reports month --month 4 --year 2026` |
| Search transactions | `mise exec uv -- uv run budy reports search grocery` |
| Show yearly overview | `mise exec uv -- uv run budy reports year --year 2026` |

## CSV imports

Budy imports **expenses** from bank CSV exports using bank-specific column mappings.

Built-in bank configs:

- `lhv`
- `seb`
- `swedbank`

If your bank is not built in, add a custom section to `config.toml`:

```toml
[banks.my_bank]
delimiter = ","
decimal = "."
encoding = "utf-8"
date_col = "Date"
amount_col = "Amount"
debit_credit_col = "Type"
debit_value = "D"
receiver_col = "Payee"
description_col = "Memo"
```

> [!TIP]
> Auto-categorization rules are applied during import by matching the combined receiver and description text case-insensitively.

## Reports

Budy includes a small but useful reporting layer:

- **`reports month`**: compare budget vs actual spending for a month
- **`reports year`**: inspect budget status across the full year
- **`reports search`**: find transactions by receiver or description
- **`reports payees`**: rank payees by spend or frequency
- **`reports weekday`**: see average spend by day of week
- **`reports volatility`**: flag unusually large transactions and overall spending variability

When your name is configured, Budy also tries to ignore transfers to yourself in reports.

## Data model notes

- Monetary amounts are stored as **integer cents**
- Transactions, budgets, categories, and category rules are persisted with `SQLModel`
- SQLite is the default database
- You can override the database with `BUDY_DB_URL`

## Development

Common project tasks:

```bash
mise run setup
mise run test
mise run typecheck
mise run build
mise run docs
mise run check
```

The full generated CLI reference lives in [docs/cli.md](docs/cli.md).
