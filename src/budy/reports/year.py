from datetime import date
from typing import Annotated, Optional

from rich.console import Console
from rich.table import Table
from sqlmodel import Session
from typer import Option, Typer

from budy.constants import MAX_YEAR, MIN_YEAR
from budy.database import engine
from budy.services.report import get_yearly_report_data
from budy.views import render_budget_status

app = Typer(no_args_is_help=True)
console = Console()


@app.command(name="year")
def show_yearly_report(
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
):
    """Show the budget status report for a specific year."""
    target_year = year or date.today().year

    with Session(engine) as session:
        monthly_reports = get_yearly_report_data(session, target_year)

    grid = Table.grid(padding=1)
    grid.add_column()
    grid.add_column()
    grid.add_column()

    panels = [
        render_budget_status(
            budget=r["budget"],
            total_spent=r["total_spent"],
            month_name=r["month_name"],
            target_year=r["target_year"],
        )
        for r in monthly_reports
    ]

    for i in range(0, len(panels), 3):
        row = panels[i : i + 3]
        row += [""] * (3 - len(row))
        grid.add_row(*row)

    console.print(f"\n[bold underline]Yearly Overview: {target_year}[/]\n")
    console.print(grid)
