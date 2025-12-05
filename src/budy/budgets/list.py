from datetime import date
from typing import Annotated

from rich.console import Console
from typer import Option, Typer

from budy.services.budget import get_budgets
from budy.views import render_budget_list, render_warning

app = Typer(no_args_is_help=True)
console = Console()


@app.command(name="list")
def read_budgets(
    target_year: Annotated[
        int,
        Option("--year", "-y", help="Filter by year."),
    ] = date.today().year,
    offset: Annotated[
        int,
        Option(
            "--offset",
            "-o",
            help="Skip the first N entries.",
        ),
    ] = 0,
    limit: Annotated[
        int,
        Option(
            "--limit",
            "-l",
            help="Limit the number of entries shown.",
        ),
    ] = 12,
) -> None:
    """Display monthly budgets in a table."""
    budgets = get_budgets(
        session=session,
        target_year=target_year,
        offset=offset,
        limit=limit,
    )
    if not budgets:
        console.print(render_warning(f"No budgets found for {target_year}."))
        return
    console.print(render_budget_list(budgets, target_year))

    # TODO:
    # indicate pagination visually so user knows if there is more hidden data


if __name__ == "__main__":
    app()
