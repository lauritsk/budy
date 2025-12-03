from rich.table import Table

from budy.models import Transaction


def render_transaction_list(transactions: list[Transaction], page_total: int) -> Table:
    """Renders a table of transactions."""
    table = Table(title="Transaction History", show_footer=True)
    table.add_column("ID", justify="right", style="dim")
    table.add_column("Entry Date", justify="right", style="cyan", footer="Page Total:")
    table.add_column("Amount", justify="right", style="green", footer=f"${page_total}")

    for transaction in transactions:
        date_str = transaction.entry_date.strftime("%b %d, %Y")
        table.add_row(str(transaction.id), date_str, f"${transaction.amount}")

    return table
