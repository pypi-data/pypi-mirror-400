"""Main CLI entry point for kabu"""

import click

from pykabu.cli.commands.config import cfg
from pykabu.cli.commands.index import index
from pykabu.cli.commands.rank import rank225
from pykabu.cli.commands.schedule import sche


@click.group()
@click.version_option()
def cli():
    """CLI tools for Japanese stock market data"""
    pass


cli.add_command(sche)
cli.add_command(index)
cli.add_command(rank225)
cli.add_command(cfg, name="config")


if __name__ == "__main__":
    cli()
