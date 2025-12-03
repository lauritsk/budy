def render_error(message: str) -> str:
    """Helper for consistent error message styling."""
    return f"\n[red bold]{message}[/]\n"


def render_warning(message: str) -> str:
    """Helper for consistent warning message styling."""
    return f"\n[yellow bold]{message}[/]\n"


def render_success(message: str) -> str:
    """Helper for consistent success message styling."""
    return f"\n[green bold]{message}[/]\n"
