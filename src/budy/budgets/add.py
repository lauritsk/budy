from datetime import date
from typing import Annotated, Optional

from rich.console import Console
from sqlmodel import Session
from typer import Exit, Option, Typer, confirm

from budy.constants import MAX_YEAR, MIN_YEAR
from budy.database import engine
from budy.services.budget import add_or_update_budget
from budy.views import render_warning

app = Typer(no_args_is_help=True)
console = Console()


def confirm_overwrite(message: str) -> bool:
    """Generic confirmation callback."""
    console.print(render_warning(message))
    return confirm("Overwrite?")


def display_result(result: dict) -> None:
    """Handles the visual output logic."""
    if result["action"] == "cancelled":
        console.print("[dim]Operation cancelled.[/]")
        raise Exit(code=0)

    new_amt = result["new_amount"] / 100.0
    target = f"{result['month_name']} {result['year']}"

    if result["action"] == "updated":
        old_amt = result["old_amount"] / 100.0
        console.print(
            f"[green]✓ Updated![/] {target}: "
            f"[strike dim]${old_amt:,.2f}[/] -> [bold green]${new_amt:,.2f}[/]"
        )
    else:
        console.print(
            f"[green]✓ Added![/] Budget for [bold]{target}[/] set to [green]${new_amt:,.2f}[/]"
        )


@app.command(name="add")
def create_budget(
    amount: Annotated[
        float,
        Option(
            "--amount",
            "-a",
            min=1,
            max=9999999,
            prompt=True,
            help="Target amount.",
        ),
    ],
    month: Annotated[
        Optional[int],
        Option(
            "--month",
            "-m",
            min=1,
            max=12,
            help="Target month.",
        ),
    ] = None,
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
    """Add a new budget to the database."""
    today = date.today()

    with Session(engine) as session:
        budget = add_or_update_budget(
            session=session,
            target_amount=amount,
            target_month=month or today.month,
            target_year=year or today.year,
            confirmation_callback=confirm_overwrite,
        )

    display_result(budget)


if __name__ == "__main__":
    app()
