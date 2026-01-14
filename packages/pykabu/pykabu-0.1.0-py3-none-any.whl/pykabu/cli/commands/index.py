"""Index command for kabu CLI"""

import click

from pykabu import config
from pykabu.sources import nikkei225
from pykabu.utils.output import TableData, print_table


@click.command()
@click.option("--plain", is_flag=True, help="Output plain text instead of rich table")
@click.option("--all", "fetch_all", is_flag=True, help="Fetch all known indices")
@click.option("--custom", is_flag=True, help="Fetch only custom configured indices")
@click.option("--merged", is_flag=True, help="Fetch default + custom indices")
def index(plain: bool, fetch_all: bool, custom: bool, merged: bool):
    """Show market indices from nikkei225jp.com

    By default, fetches the 8 standard indices. Use --all to fetch all known
    indices, or configure custom indices with 'kabu config index add'.
    """
    # Determine which codes to fetch
    if fetch_all:
        index_codes = nikkei225.get_all_known_indices()
        title = "All Market Indices"
    elif custom:
        index_codes = config.get_custom_indices()
        if not index_codes:
            click.echo("No custom indices configured.")
            click.echo("Use 'kabu config index add CODE' to add some.")
            click.echo("Run 'kabu config index list' to see available codes.")
            return
        title = "Custom Market Indices"
    elif merged:
        index_codes = {**nikkei225.get_default_indices(), **config.get_custom_indices()}
        title = "Market Indices (Default + Custom)"
    else:
        index_codes = nikkei225.get_default_indices()
        title = "Market Indices"

    items = nikkei225.get_indices(index_codes)

    if not items:
        click.echo("No data found.")
        return

    data = TableData(
        title=title,
        columns=["Name", "Value", "Change", "%"],
        rows=[[item.name, item.value, item.change, item.percent] for item in items],
    )

    print_table(data, plain=plain)
