# budy

An itsy bitsy CLI budgeting assistant for tracking spending, budgets, and bank statement imports from the terminal.

This is a small local-first Python application. It stores data in SQLite, imports bank CSV exports, and provides basic budget and spending reports.

## What it does

- Imports expense transactions from bank CSV exports
- Includes built-in import mappings for LHV, SEB, and Swedbank
- Supports custom bank import formats through `config.toml`
- Stores transactions, categories, budgets, and category rules in SQLite
- Provides commands for adding, editing, listing, searching, and exporting transactions
- Supports monthly budgets and budget suggestions based on spending history
- Generates reports for monthly spending, yearly spending, payees, weekdays, and spending volatility

## Code layout

```text
src/budy/
  __init__.py       CLI entrypoint and command registration
  config.py         application configuration and default paths
  database.py       SQLite/SQLModel database setup
  schemas.py        database models
  setup.py          interactive first-run setup
  importer.py       bank CSV import logic
  transactions.py   transaction commands
  categories.py     category and auto-categorization commands
  budgets.py        budget commands and budget generation
  reports.py        spending and budget reports

tests/              pytest test suite
```

## Main CLI areas

```bash
budy setup
budy transactions --help
budy categories --help
budy budgets --help
budy reports --help
```

## Data storage

By default, Budy stores `config.toml` and `budy.db` in the platform app-data directory. The database URL can be overridden with `BUDY_DB_URL`.

Monetary amounts are stored as integer cents. Data is modeled with SQLModel and persisted to SQLite by default.

## CSV imports

Budy imports expenses from bank CSV exports using bank-specific column mappings.

Built-in bank configs:

- `lhv`
- `seb`
- `swedbank`

Custom bank formats can be added in `config.toml`:

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

Auto-categorization rules are applied during import by matching receiver and description text case-insensitively.

## Reports

Available report commands include:

- `reports month`
- `reports year`
- `reports search`
- `reports payees`
- `reports weekday`
- `reports volatility`
