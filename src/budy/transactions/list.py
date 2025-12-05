from typing import Annotated

from rich.console import Console
from sqlmodel import Session
from typer import Option, Typer

from budy.database import engine
from budy.services.transaction import get_transactions
from budy.views import render_transaction_list, render_warning

app = Typer(no_args_is_help=True)
console = Console()


@app.command(name="list")
def read_transactions(
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
    ] = 7,
) -> None:
    """Display transaction history in a table."""
    with Session(engine) as session:
        transactions = get_transactions(session=session, offset=offset, limit=limit)

    if not transactions:
        console.print(
            render_warning(message="No transactions found for the selected dates.")
        )
        return

    console.print(render_transaction_list(daily_transactions=transactions))


if __name__ == "__main__":
    app()
