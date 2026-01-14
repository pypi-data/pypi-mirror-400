"""Rank command for kabu CLI"""

import click

from pykabu.sources import nikkei225
from pykabu.utils.output import TableData, print_table


@click.command()
@click.option("--plain", is_flag=True, help="Output plain text instead of rich table")
@click.option("--top", "show_top", is_flag=True, help="Show only top contributors")
@click.option("--bottom", "show_bottom", is_flag=True, help="Show only bottom contributors")
def rank225(plain: bool, show_top: bool, show_bottom: bool):
    """Show Nikkei 225 contribution ranking (寄与度ランキング)"""
    top_items, bottom_items = nikkei225.get_rank225()

    # Default: show both if neither flag specified
    if not show_top and not show_bottom:
        show_top = True
        show_bottom = True

    if show_top:
        if not top_items:
            click.echo("No top contributors data found.")
        else:
            data = TableData(
                title="寄与度上位 (Top Contributors)",
                columns=["銘柄", "寄与度", "現在値", "前日比"],
                rows=[
                    [item.name, item.contribution, item.price, item.change]
                    for item in top_items
                ],
            )
            print_table(data, plain=plain)

        if show_bottom:
            click.echo()  # Separator between tables

    if show_bottom:
        if not bottom_items:
            click.echo("No bottom contributors data found.")
        else:
            data = TableData(
                title="寄与度下位 (Bottom Contributors)",
                columns=["銘柄", "寄与度", "現在値", "前日比"],
                rows=[
                    [item.name, item.contribution, item.price, item.change]
                    for item in bottom_items
                ],
            )
            print_table(data, plain=plain)
