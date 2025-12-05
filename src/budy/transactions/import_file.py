from pathlib import Path
from typing import Annotated

from rich.console import Console
from typer import Exit, Option, Typer

from budy.constants import Bank
from budy.services.transaction import import_transactions
from budy.views import render_error, render_success, render_warning

app = Typer(no_args_is_help=True)
console = Console()


def display_summary(transactions: list, filename: str, dry_run: bool) -> None:
    """Handles the post-import reporting logic."""
    if not transactions:
        console.print(render_warning(f"No valid expenses found in {filename}."))
        return

    count = len(transactions)
    total_display = sum(t.amount for t in transactions) / 100.0

    console.print(
        f"\nFound [bold]{count}[/] transactions totaling [green]${total_display:,.2f}[/]."
    )

    if dry_run:
        console.print("[yellow]Dry run active. No changes made to database.[/]")
    else:
        console.print(render_success(f"Successfully imported {count} transactions!"))


@app.command(name="import")
def run_import(
    bank: Annotated[
        Bank,
        Option(
            "--bank",
            "-b",
            prompt=True,
            help="The bank to import from.",
            case_sensitive=False,
        ),
    ],
    file_path: Annotated[
        Path,
        Option(
            "--file",
            "-f",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
            prompt=True,
            help="Path to the CSV file.",
        ),
    ],
    dry_run: Annotated[
        bool,
        Option(
            help="Parse the file but do not save to the database.",
        ),
    ] = False,
) -> None:
    """Import transactions from a bank CSV file."""
    console.print(
        f"Parsing [bold]{file_path.name}[/] using [cyan]{bank.value}[/] importer..."
    )

    try:
        transactions = import_transactions(
            session=session,
            bank=bank,
            file_path=file_path,
            dry_run=dry_run,
        )
    except ValueError as e:
        console.print(render_error(str(e)))
        raise Exit(1)
    except Exception as e:
        console.print(render_error(f"Unexpected error: {e}"))
        raise Exit(1)

    display_summary(transactions, file_path.name, dry_run)


if __name__ == "__main__":
    app()
