from rich.console import Console
from rich.table import Table
from sqlmodel import Session
from typer import Typer

from budy.database import engine
from budy.services.report import get_weekday_report_data
from budy.views import render_warning

app = Typer(no_args_is_help=True)
console = Console()


@app.command(name="weekday")
def show_weekday_report() -> None:
    """Analyze spending habits by day of the week."""
    with Session(engine) as session:
        report_data = get_weekday_report_data(session)

    if not report_data:
        console.print(render_warning("No transactions found to analyze."))
        return

    total_spent = sum(d["total_amount"] for d in report_data)
    total_count = sum(d["count"] for d in report_data)

    table = Table(title="Spending Habits by Day of Week", show_footer=True)
    table.add_column("Day", style="cyan", footer="TOTAL")
    table.add_column("Avg Transaction", justify="right", style="green")
    table.add_column("Count", justify="right", style="dim", footer=str(total_count))
    table.add_column(
        "Total Spent",
        justify="right",
        style="bold",
        footer=f"${total_spent / 100:,.2f}",
    )

    for day in report_data:
        if day["count"] == 0:
            table.add_row(day["day_name"], "-", "0", "-")
        else:
            table.add_row(
                day["day_name"],
                f"${day['avg_amount'] / 100:,.2f}",
                str(day["count"]),
                f"${day['total_amount'] / 100:,.2f}",
            )

    console.print(table)
