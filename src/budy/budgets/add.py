import calendar
from datetime import date
from typing import Annotated, Optional

from rich.console import Console
from sqlmodel import Session, select
from typer import Exit, Option, Typer, confirm

from budy.constants import MAX_YEAR, MIN_YEAR
from budy.database import engine
from budy.models import Budget
from budy.views import render_warning

app = Typer(no_args_is_help=True)
console = Console()


@app.command(name="add")
@app.command(name="a", hidden=True)
def create_budget(
    target_amount: Annotated[
        int,
        Option(
            "--amount",
            "-a",
            min=1,
            max=9999999,
            prompt=True,
            help="Set the budget target amount.",
        ),
    ],
    target_month: Annotated[
        Optional[int],
        Option(
            "--month",
            "-m",
            min=1,
            max=12,
            help="Set the budget target month.",
        ),
    ] = None,
    target_year: Annotated[
        Optional[int],
        Option(
            "--year",
            "-y",
            min=MIN_YEAR,
            max=MAX_YEAR,
            help="Set the budget target year.",
        ),
    ] = None,
) -> None:
    """Add a new budget to the database."""
    with Session(engine) as session:
        current_date = date.today()
        final_target_month = target_month if target_month else current_date.month
        final_target_year = target_year if target_year else current_date.year

        month_name = calendar.month_name[final_target_month]

        existing_budget = session.exec(
            select(Budget).where(
                Budget.target_year == final_target_year,
                Budget.target_month == final_target_month,
            )
        ).first()

        if existing_budget:
            console.print(
                render_warning(
                    f"A budget for [b]{month_name} {final_target_year}[/] already exists."
                )
            )
            console.print(
                f"Change: [red]${existing_budget.amount}[/] -> [green]${target_amount}[/]\n"
            )

            if not confirm(f"Overwrite the {month_name} budget?"):
                print("[dim]Operation cancelled.[/]")
                raise Exit(code=0)

            old_amount = existing_budget.amount

            existing_budget.amount = target_amount
            session.add(existing_budget)
            session.commit()
            session.refresh(existing_budget)

            print(
                f"[green]✓ Updated![/] {month_name} {final_target_year}: "
                f"[strike dim]${old_amount}[/] -> [bold green]${target_amount}[/]"
            )
            return

        budget = Budget(
            amount=target_amount,
            target_month=final_target_month,
            target_year=final_target_year,
        )

        session.add(budget)
        session.commit()
        session.refresh(budget)

        print(
            f"[green]✓ Added![/] Budget for [bold]{month_name} {final_target_year}[/] set to [green]${target_amount}[/]"
        )


if __name__ == "__main__":
    app()
