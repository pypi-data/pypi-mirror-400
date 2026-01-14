"""Sector ranking command for kabu CLI"""

import click

from pykabu.sources import nikkei225
from pykabu.utils.output import TableData, print_table


@click.command()
@click.option("--plain", is_flag=True, help="Output plain text instead of rich table")
@click.option("--top", "show_top", is_flag=True, help="Show only top gainers")
@click.option("--bottom", "show_bottom", is_flag=True, help="Show only top losers")
def rank_sec(plain: bool, show_top: bool, show_bottom: bool):
    """Show sector ranking (業種別株価指数ランキング)"""
    gainers, losers = nikkei225.get_sector_rank()

    # Default: show both if neither flag specified
    if not show_top and not show_bottom:
        show_top = True
        show_bottom = True

    if show_top:
        if not gainers:
            click.echo("No top gainers data found.")
        else:
            data = TableData(
                title="値上がり率 TOP10 (Top Gainers)",
                columns=["変動率", "業種"],
                rows=[
                    [item.change, item.name]
                    for item in gainers
                ],
            )
            print_table(data, plain=plain)

        if show_bottom:
            click.echo()  # Separator between tables

    if show_bottom:
        if not losers:
            click.echo("No top losers data found.")
        else:
            data = TableData(
                title="値下がり率 TOP10 (Top Losers)",
                columns=["変動率", "業種"],
                rows=[
                    [item.change, item.name]
                    for item in losers
                ],
            )
            print_table(data, plain=plain)
