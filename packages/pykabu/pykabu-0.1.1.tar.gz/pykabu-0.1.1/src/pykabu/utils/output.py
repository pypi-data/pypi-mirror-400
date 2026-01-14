"""Output formatting utilities supporting both rich and plain text output"""

from dataclasses import dataclass
from typing import Any

from rich.console import Console
from rich.table import Table


@dataclass
class TableData:
    """Data structure for tabular output"""
    title: str
    columns: list[str]
    rows: list[list[Any]]


def print_table(data: TableData, plain: bool = False) -> None:
    """Print tabular data in rich or plain format.

    Args:
        data: TableData containing title, columns, and rows
        plain: If True, output plain text; otherwise use rich formatting
    """
    if plain:
        _print_plain(data)
    else:
        _print_rich(data)


def _print_rich(data: TableData) -> None:
    """Print table using rich formatting with colors"""
    console = Console()

    table = Table(title=data.title, show_header=True, header_style="bold cyan")

    for column in data.columns:
        table.add_column(column)

    for row in data.rows:
        styled_row = []
        for i, cell in enumerate(row):
            cell_str = str(cell) if cell is not None else "-"
            # Color importance column (column with stars)
            if "★" in cell_str:
                star_count = cell_str.count("★")
                if star_count >= 4:
                    cell_str = f"[bold red]{cell_str}[/bold red]"
                elif star_count >= 3:
                    cell_str = f"[yellow]{cell_str}[/yellow]"
                else:
                    cell_str = f"[dim]{cell_str}[/dim]"
            styled_row.append(cell_str)
        table.add_row(*styled_row)

    console.print(table)


def _print_plain(data: TableData) -> None:
    """Print table as plain text, pipe-friendly"""
    print(f"# {data.title}")
    print()

    # Calculate column widths
    widths = [len(col) for col in data.columns]
    for row in data.rows:
        for i, cell in enumerate(row):
            cell_str = str(cell) if cell is not None else "-"
            widths[i] = max(widths[i], len(cell_str))

    # Print header
    header = " | ".join(col.ljust(widths[i]) for i, col in enumerate(data.columns))
    print(header)
    print("-" * len(header))

    # Print rows
    for row in data.rows:
        row_str = " | ".join(
            (str(cell) if cell is not None else "-").ljust(widths[i])
            for i, cell in enumerate(row)
        )
        print(row_str)
