"""Schedule command for kabu CLI"""

import click

from pykabu import config
from pykabu.sources import nikkei225
from pykabu.utils.output import TableData, print_table


@click.command()
@click.option("-t", "--tomorrow", is_flag=True, help="Show tomorrow's schedule")
@click.option("-w", "--week", is_flag=True, help="Show this week's schedule")
@click.option("-i", "--importance", type=int, default=None, help="Minimum importance (1-5 stars)")
@click.option("--plain", is_flag=True, help="Output plain text instead of rich table")
def sche(tomorrow: bool, week: bool, importance: int | None, plain: bool):
    """Show economic schedule from nikkei225jp.com"""
    # Use config default if not specified
    if importance is None:
        importance = config.get("default_importance", 0)

    if week:
        items = nikkei225.get_week_schedule()
        title = "This Week's Economic Schedule"
    elif tomorrow:
        items = nikkei225.get_tomorrow_schedule()
        title = "Tomorrow's Economic Schedule"
    else:
        items = nikkei225.get_today_schedule()
        title = "Today's Economic Schedule"

    if importance > 0:
        items = nikkei225.filter_schedule_by_importance(items, importance)
        title += f" (★{importance}+)"

    if not items:
        click.echo("No schedule items found.")
        return

    data = TableData(
        title=title,
        columns=["Date", "Time", "Importance", "Indicator", "Result", "Forecast", "Previous"],
        rows=[
            [item.date_str, item.time, item.importance, item.indicator,
             item.result, item.forecast, item.previous]
            for item in items
        ],
    )

    print_table(data, plain=plain)
