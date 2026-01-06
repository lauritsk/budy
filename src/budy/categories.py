from typing import Annotated

from rich.console import Console
from sqlmodel import Session
from typer import Argument, Exit, Option, Typer, confirm

from budy.database import engine
from budy.services.category import (
    create_category,
    create_rule,
    delete_category,
    delete_rule,
    get_categories,
    get_rules,
)
from budy.views.category import render_category_list, render_rule_list
from budy.views.messages import render_error, render_success, render_warning

app = Typer(no_args_is_help=True)
rules_app = Typer(
    name="rules", help="Manage auto-categorization rules.", no_args_is_help=True
)
app.add_typer(rules_app)
console = Console()


@app.command(name="list")
def list_categories_cmd():
    """List all transaction categories."""
    with Session(engine) as session:
        categories = get_categories(session=session)

    if not categories:
        console.print(render_warning(message="No categories found."))
        return

    console.print(render_category_list(categories))


@app.command(name="add")
def add_category_cmd(
    name: Annotated[str, Argument(help="Name of the category.")],
    color: Annotated[
        str,
        Option(
            "--color", "-c", help="Color for the category (e.g. red, blue, #ff0000)."
        ),
    ] = "white",
):
    """Add a new transaction category."""
    try:
        with Session(engine) as session:
            category = create_category(session=session, name=name, color=color)
        console.print(
            render_success(
                message=f"Added category [bold]{category.name}[/] ({category.color})"
            )
        )
    except Exception as e:
        console.print(render_error(message=f"Error adding category: {e}"))
        raise Exit(1)


@app.command(name="delete")
def delete_category_cmd(
    category_id: Annotated[int, Argument(help="ID of the category to delete.")],
    force: Annotated[
        bool,
        Option(
            "--force",
            "-f",
            help="Force delete without confirmation.",
        ),
    ] = False,
):
    """Delete a transaction category."""
    if not force:
        if not confirm(f"Are you sure you want to delete category #{category_id}?"):
            raise Exit()

    with Session(engine) as session:
        success = delete_category(session=session, category_id=category_id)

    if not success:
        console.print(render_error(message=f"Category #{category_id} not found."))
        raise Exit(1)

    console.print(render_success(message=f"Deleted category [bold]#{category_id}[/]"))


# --- Rules Sub-Commands ---


@rules_app.command(name="list")
def list_rules_cmd():
    """List all auto-categorization rules."""
    with Session(engine) as session:
        rules = get_rules(session=session)

    if not rules:
        console.print(render_warning(message="No rules found."))
        return

    console.print(render_rule_list(rules))


@rules_app.command(name="add")
def add_rule_cmd(
    pattern: Annotated[
        str, Argument(help="Keyword pattern to match (case-insensitive).")
    ],
    category_id: Annotated[
        int, Option("--category-id", "-c", help="ID of the category to assign.")
    ],
):
    """Add a new auto-categorization rule."""
    try:
        with Session(engine) as session:
            rule = create_rule(
                session=session, pattern=pattern, category_id=category_id
            )
        console.print(
            render_success(
                message=f"Added rule: '{rule.pattern}' -> Category #{rule.category_id}"
            )
        )
    except Exception as e:
        console.print(render_error(message=f"Error adding rule: {e}"))
        raise Exit(1)


@rules_app.command(name="delete")
def delete_rule_cmd(
    rule_id: Annotated[int, Argument(help="ID of the rule to delete.")],
    force: Annotated[
        bool,
        Option(
            "--force",
            "-f",
            help="Force delete without confirmation.",
        ),
    ] = False,
):
    """Delete a rule."""
    if not force:
        if not confirm(f"Are you sure you want to delete rule #{rule_id}?"):
            raise Exit()

    with Session(engine) as session:
        success = delete_rule(session=session, rule_id=rule_id)

    if not success:
        console.print(render_error(message=f"Rule #{rule_id} not found."))
        raise Exit(1)

    console.print(render_success(message=f"Deleted rule [bold]#{rule_id}[/]"))
