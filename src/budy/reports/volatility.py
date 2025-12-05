from typing import Annotated, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from sqlmodel import Session
from typer import Option, Typer

from budy.constants import MAX_YEAR, MIN_YEAR
from budy.database import engine
from budy.services.report import get_volatility_report_data
from budy.views import render_simple_transaction_list, render_warning

app = Typer(no_args_is_help=True)
console = Console()


@app.command(name="volatility")
def show_volatility_report(
    year: Annotated[
        Optional[int],
        Option(
            "--year",
            "-y",
            min=MIN_YEAR,
            max=MAX_YEAR,
            help="Target year.",
        ),
    ] = None,
) -> None:
    """Analyze spending volatility and outliers."""
    with Session(engine) as session:
        data = get_volatility_report_data(session, year)

    if not data:
        console.print(render_warning("No transactions found."))
        return

    count, avg, stdev = data["total_count"], data["avg_amount"], data["stdev_amount"]

    cv = (stdev / avg) if avg else 0
    if cv > 1.5:
        volatility_msg = "[red]High Volatility[/]"
    elif cv < 0.5:
        volatility_msg = "[green]Low Volatility[/]"
    else:
        volatility_msg = "[yellow]Moderate Volatility[/]"

    grid = Table.grid(padding=(0, 2))
    grid.add_column(style="dim")
    grid.add_column(justify="right", style="bold")
    grid.add_row("Total Transactions:", str(count))
    grid.add_row("Average Amount:", f"${avg / 100:,.2f}")
    grid.add_row("Standard Deviation:", f"${stdev / 100:,.2f}")

    console.print(
        Panel(
            grid,
            title=f"Volatility Analysis {'(' + str(year) + ')' if year else '(All Time)'}",
            subtitle=volatility_msg,
            expand=False,
        )
    )
    console.print("")
    console.print(
        render_simple_transaction_list(
            data["outliers"], title="Top 5 Highest Transactions"
        )
    )
