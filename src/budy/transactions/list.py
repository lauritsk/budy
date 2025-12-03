from typing import Annotated

from rich.console import Console
from sqlmodel import Session, desc, select
from typer import Option, Typer

from budy.database import engine
from budy.models import Transaction
from budy.views import render_transaction_list, render_warning

app = Typer(no_args_is_help=True)
console = Console()


@app.command(name="list")
@app.command(name="ls", hidden=True)
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
        transactions = list(
            session.exec(
                select(Transaction)
                .order_by(desc(Transaction.entry_date))
                .offset(offset)
                .limit(limit)
            ).all()
        )

        if not transactions:
            console.print(render_warning("No transactions found."))
            return

        page_total = sum(t.amount for t in transactions)

        console.print(render_transaction_list(transactions, page_total))


if __name__ == "__main__":
    app()
