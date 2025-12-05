from typing import Annotated

from rich.console import Console
from rich.table import Table
from sqlmodel import Session
from typer import Argument, Option, Typer

from budy.database import engine
from budy.services.transaction import search_transactions
from budy.views import render_warning

app = Typer(no_args_is_help=True)
console = Console()


@app.command(name="search")
def run_search(
    query: Annotated[
        str,
        Argument(help="Keyword to search for (in receiver or description)."),
    ],
    limit: Annotated[
        int,
        Option(
            "--limit",
            "-l",
            min=1,
            help="Maximum number of results to display.",
        ),
    ] = 20,
) -> None:
    """Search transactions by keyword in receiver or description."""
    with Session(engine) as session:
        results = search_transactions(session, query, limit)

    if not results:
        console.print(render_warning(f"No transactions found matching '{query}'."))
        return

    display_results = results[::-1]
    total_cents = sum(t.amount for t in display_results)

    title = f"Search Results: '{query}'"
    if len(results) == limit:
        title += f" (Showing latest {limit})"

    table = Table(title=title, show_footer=True)
    table.add_column("Date", style="cyan")
    table.add_column("Receiver", style="white")
    table.add_column("Description", style="dim", footer="Total:")
    table.add_column(
        "Amount",
        justify="right",
        style="red bold",
        footer=f"${total_cents / 100:,.2f}",
    )

    for t in display_results:
        desc = t.description or ""
        if len(desc) > 30:
            desc = f"{desc[:27]}..."

        table.add_row(
            t.entry_date.strftime("%b %d, %Y"),
            t.receiver or "[dim]-[/]",
            desc,
            f"${t.amount / 100:,.2f}",
        )

    console.print(table)
