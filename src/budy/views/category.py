from rich.table import Table

from budy.schemas import Category, CategoryRule


def render_category_list(categories: list[Category]) -> Table:
    """Renders a list of categories in a table."""
    table = Table(title="Transaction Categories")

    table.add_column("ID", style="dim", width=4)
    table.add_column("Name", style="bold")
    table.add_column("Color")

    for cat in categories:
        color_style = cat.color if cat.color else "white"
        table.add_row(
            str(cat.id),
            cat.name,
            f"[{color_style}]■[/] {cat.color}",
        )

    return table


def render_rule_list(rules: list[tuple[CategoryRule, Category]]) -> Table:
    """Renders a list of categorization rules."""
    table = Table(title="Auto-Categorization Rules")

    table.add_column("ID", style="dim", width=4)
    table.add_column("Pattern", style="cyan")
    table.add_column("Assigns To", style="bold")

    for rule, category in rules:
        color_style = category.color if category.color else "white"
        table.add_row(
            str(rule.id),
            rule.pattern,
            f"[{color_style}]{category.name}[/]",
        )

    return table
