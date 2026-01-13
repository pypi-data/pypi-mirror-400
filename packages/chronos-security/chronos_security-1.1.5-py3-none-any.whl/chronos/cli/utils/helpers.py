"""
CHRONOS CLI Utilities
=====================

Helper functions and utilities for the CLI module.
"""

import sys
from contextlib import contextmanager
from typing import Generator, Optional

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn


class ChronosCLIError(Exception):
    """Base exception for CLI errors."""
    
    def __init__(self, message: str, hint: Optional[str] = None):
        self.message = message
        self.hint = hint
        super().__init__(self.message)


class ConfigurationError(ChronosCLIError):
    """Configuration-related CLI error."""
    pass


class ScanError(ChronosCLIError):
    """Scan operation error."""
    pass


class AnalysisError(ChronosCLIError):
    """Analysis operation error."""
    pass


class DefenseError(ChronosCLIError):
    """Defense operation error."""
    pass


@contextmanager
def error_handler(console: Console) -> Generator[None, None, None]:
    """Context manager for handling CLI errors gracefully.
    
    Args:
        console: Rich console for output.
        
    Yields:
        None
        
    Example:
        with error_handler(console):
            do_something_risky()
    """
    try:
        yield
    except ChronosCLIError as e:
        console.print(Panel(
            f"[bold red]Error:[/bold red] {e.message}\n"
            + (f"\n[yellow]Hint:[/yellow] {e.hint}" if e.hint else ""),
            title="CHRONOS Error",
            border_style="red",
        ))
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled.[/yellow]")
        sys.exit(130)
    except FileNotFoundError as e:
        console.print(f"[red]File not found:[/red] {e.filename}")
        sys.exit(1)
    except PermissionError as e:
        console.print(f"[red]Permission denied:[/red] {e.filename}")
        sys.exit(1)


def create_progress(console: Console) -> Progress:
    """Create a styled progress bar.
    
    Args:
        console: Rich console instance.
        
    Returns:
        Configured Progress instance.
    """
    return Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=40),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
    )


def print_success(console: Console, message: str, title: str = "Success") -> None:
    """Print a success message in a panel.
    
    Args:
        console: Rich console instance.
        message: Message to display.
        title: Panel title.
    """
    console.print(Panel(
        f"[green]✓[/green] {message}",
        title=title,
        border_style="green",
    ))


def print_warning(console: Console, message: str, title: str = "Warning") -> None:
    """Print a warning message in a panel.
    
    Args:
        console: Rich console instance.
        message: Message to display.
        title: Panel title.
    """
    console.print(Panel(
        f"[yellow]⚠[/yellow] {message}",
        title=title,
        border_style="yellow",
    ))


def print_error(console: Console, message: str, title: str = "Error") -> None:
    """Print an error message in a panel.
    
    Args:
        console: Rich console instance.
        message: Message to display.
        title: Panel title.
    """
    console.print(Panel(
        f"[red]✗[/red] {message}",
        title=title,
        border_style="red",
    ))


def confirm_action(console: Console, message: str, default: bool = False) -> bool:
    """Ask for user confirmation.
    
    Args:
        console: Rich console instance.
        message: Confirmation message.
        default: Default value if user presses Enter.
        
    Returns:
        True if confirmed, False otherwise.
    """
    suffix = "[Y/n]" if default else "[y/N]"
    response = console.input(f"[yellow]?[/yellow] {message} {suffix}: ").strip().lower()
    
    if not response:
        return default
    return response in ("y", "yes")
