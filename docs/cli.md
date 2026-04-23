# `budy`

An itsy bitsy CLI budgeting assistant.

**Usage**:

```console
$ budy [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `setup`: Initialize the configuration file with...
* `transactions`: Manage transaction history.
* `budgets`: Set and manage monthly targets.
* `categories`
* `reports`: View financial insights.

## `budy setup`

Initialize the configuration file with your details.

**Usage**:

```console
$ budy setup [OPTIONS]
```

**Options**:

* `--first-name TEXT`: Your first name.
* `--last-name TEXT`: Your last name.
* `--help`: Show this message and exit.

## `budy transactions`

Manage transaction history.

**Usage**:

```console
$ budy transactions [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `add`: Add a new transaction to the database.
* `list`: Display transaction history in a table.
* `update`: Update an existing transaction.
* `delete`: Delete a transaction.
* `export`: Export transactions to CSV or JSON.
* `import`: Import transactions from a bank CSV file.

### `budy transactions add`

Add a new transaction to the database.

**Usage**:

```console
$ budy transactions add [OPTIONS]
```

**Options**:

* `-a, --amount FLOAT RANGE`: Set the transaction amount (in dollars/euros).  [0.01&lt;=x&lt;=9999999; required]
* `-d, --date [%Y-%m-%d|%Y/%m/%d]`: Set the transaction date (YYYY-MM-DD).
* `-c, --category INTEGER`: Category ID.
* `--help`: Show this message and exit.

### `budy transactions list`

Display transaction history in a table.

**Usage**:

```console
$ budy transactions list [OPTIONS]
```

**Options**:

* `-o, --offset INTEGER`: Skip the first N entries.  [default: 0]
* `-l, --limit INTEGER`: Limit the number of entries shown.  [default: 7]
* `--help`: Show this message and exit.

### `budy transactions update`

Update an existing transaction.

**Usage**:

```console
$ budy transactions update [OPTIONS] TRANSACTION_ID
```

**Arguments**:

* `TRANSACTION_ID`: ID of the transaction to update.  [required]

**Options**:

* `-a, --amount FLOAT RANGE`: New amount.  [0.01&lt;=x&lt;=9999999]
* `-d, --date [%Y-%m-%d|%Y/%m/%d]`: New date (YYYY-MM-DD).
* `-r, --receiver TEXT`: New receiver/payee.
* `--description, --desc TEXT`: New description.
* `-c, --category INTEGER`: New Category ID.
* `--help`: Show this message and exit.

### `budy transactions delete`

Delete a transaction.

**Usage**:

```console
$ budy transactions delete [OPTIONS] TRANSACTION_ID
```

**Arguments**:

* `TRANSACTION_ID`: ID of the transaction to delete.  [required]

**Options**:

* `-f, --force`: Force delete without confirmation.
* `--help`: Show this message and exit.

### `budy transactions export`

Export transactions to CSV or JSON.

**Usage**:

```console
$ budy transactions export [OPTIONS]
```

**Options**:

* `-o, --output PATH`: Path to save the export file.  [required]
* `-f, --format TEXT`: Output format (csv, json).  [default: csv]
* `--help`: Show this message and exit.

### `budy transactions import`

Import transactions from a bank CSV file.

**Usage**:

```console
$ budy transactions import [OPTIONS]
```

**Options**:

* `-b, --bank TEXT`: The bank to import from (defined in config).  [required]
* `-f, --file FILE`: Path to the CSV file.  [required]
* `--dry-run / --no-dry-run`: Parse the file but do not save to the database.  [default: no-dry-run]
* `--help`: Show this message and exit.

## `budy budgets`

Set and manage monthly targets.

**Usage**:

```console
$ budy budgets [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `add`: Add a new budget to the database.
* `list`: Display monthly budgets in a table.
* `generate`: Auto-generate monthly budgets based on...

### `budy budgets add`

Add a new budget to the database.

**Usage**:

```console
$ budy budgets add [OPTIONS]
```

**Options**:

* `-a, --amount FLOAT RANGE`: Target amount.  [1&lt;=x&lt;=9999999; required]
* `-m, --month INTEGER RANGE`: Target month.  [1&lt;=x&lt;=12]
* `-y, --year INTEGER RANGE`: Target year.  [1900&lt;=x&lt;=2100]
* `--help`: Show this message and exit.

### `budy budgets list`

Display monthly budgets in a table.

**Usage**:

```console
$ budy budgets list [OPTIONS]
```

**Options**:

* `-y, --year INTEGER`: Filter by year.  [default: 2026]
* `-o, --offset INTEGER`: Skip the first N entries.  [default: 0]
* `-l, --limit INTEGER`: Limit the number of entries shown.  [default: 12]
* `--help`: Show this message and exit.

### `budy budgets generate`

Auto-generate monthly budgets based on historical transaction data.

**Usage**:

```console
$ budy budgets generate [OPTIONS]
```

**Options**:

* `-y, --year INTEGER RANGE`: Target year.  [1900&lt;=x&lt;=2100]
* `-f, --force`: Overwrite existing budgets without asking.
* `--yes`: Skip confirmation prompt.
* `--help`: Show this message and exit.

## `budy categories`

**Usage**:

```console
$ budy categories [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `list`: List all transaction categories.
* `add`: Add a new transaction category.
* `delete`: Delete a transaction category.
* `rules`: Manage auto-categorization rules.

### `budy categories list`

List all transaction categories.

**Usage**:

```console
$ budy categories list [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `budy categories add`

Add a new transaction category.

**Usage**:

```console
$ budy categories add [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Name of the category.  [required]

**Options**:

* `-c, --color TEXT`: Color for the category (e.g. red, blue, #ff0000).  [default: white]
* `--help`: Show this message and exit.

### `budy categories delete`

Delete a transaction category.

**Usage**:

```console
$ budy categories delete [OPTIONS] CATEGORY_ID
```

**Arguments**:

* `CATEGORY_ID`: ID of the category to delete.  [required]

**Options**:

* `-f, --force`: Force delete without confirmation.
* `--help`: Show this message and exit.

### `budy categories rules`

Manage auto-categorization rules.

**Usage**:

```console
$ budy categories rules [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `list`: List all auto-categorization rules.
* `add`: Add a new auto-categorization rule.
* `delete`: Delete a rule.

#### `budy categories rules list`

List all auto-categorization rules.

**Usage**:

```console
$ budy categories rules list [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `budy categories rules add`

Add a new auto-categorization rule.

**Usage**:

```console
$ budy categories rules add [OPTIONS] PATTERN
```

**Arguments**:

* `PATTERN`: Keyword pattern to match (case-insensitive).  [required]

**Options**:

* `-c, --category-id INTEGER`: ID of the category to assign.  [required]
* `--help`: Show this message and exit.

#### `budy categories rules delete`

Delete a rule.

**Usage**:

```console
$ budy categories rules delete [OPTIONS] RULE_ID
```

**Arguments**:

* `RULE_ID`: ID of the rule to delete.  [required]

**Options**:

* `-f, --force`: Force delete without confirmation.
* `--help`: Show this message and exit.

## `budy reports`

View financial insights.

**Usage**:

```console
$ budy reports [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `month`: Show the budget status report for a...
* `search`: Search transactions by keyword in receiver...
* `payees`: Rank payees by total spending or frequency.
* `volatility`: Analyze spending volatility and outliers.
* `weekday`: Analyze spending habits by day of the week.
* `year`: Show the budget status report for a...

### `budy reports month`

Show the budget status report for a specific month.

**Usage**:

```console
$ budy reports month [OPTIONS]
```

**Options**:

* `-m, --month INTEGER RANGE`: Target month.  [1&lt;=x&lt;=12]
* `-y, --year INTEGER RANGE`: Target year.  [1900&lt;=x&lt;=2100]
* `--help`: Show this message and exit.

### `budy reports search`

Search transactions by keyword in receiver or description.

**Usage**:

```console
$ budy reports search [OPTIONS] QUERY
```

**Arguments**:

* `QUERY`: Keyword to search for (in receiver or description).  [required]

**Options**:

* `-l, --limit INTEGER RANGE`: Maximum number of results to display.  [default: 20; x&gt;=1]
* `--help`: Show this message and exit.

### `budy reports payees`

Rank payees by total spending or frequency.

**Usage**:

```console
$ budy reports payees [OPTIONS]
```

**Options**:

* `-y, --year INTEGER RANGE`: Target year.  [1900&lt;=x&lt;=2100]
* `-l, --limit INTEGER`: Number of payees to show.  [default: 10]
* `-c, --by-count`: Sort by transaction count instead of total amount.
* `--help`: Show this message and exit.

### `budy reports volatility`

Analyze spending volatility and outliers.

**Usage**:

```console
$ budy reports volatility [OPTIONS]
```

**Options**:

* `-y, --year INTEGER RANGE`: Target year.  [1900&lt;=x&lt;=2100]
* `--help`: Show this message and exit.

### `budy reports weekday`

Analyze spending habits by day of the week.

**Usage**:

```console
$ budy reports weekday [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `budy reports year`

Show the budget status report for a specific year.

**Usage**:

```console
$ budy reports year [OPTIONS]
```

**Options**:

* `-y, --year INTEGER RANGE`: Target year.  [1900&lt;=x&lt;=2100]
* `--help`: Show this message and exit.
