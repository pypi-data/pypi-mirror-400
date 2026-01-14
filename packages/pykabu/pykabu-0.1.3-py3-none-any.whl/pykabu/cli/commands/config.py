"""Config command for kabu CLI"""

import click

from pykabu import config


@click.group()
def cfg():
    """Manage pykabu configuration"""
    pass


@cfg.command("show")
def show():
    """Show current configuration"""
    current = config.load_config()
    click.echo(f"Config file: {config.get_config_path()}")
    click.echo()
    for key, value in current.items():
        click.echo(f"  {key}: {value}")


@cfg.command("set")
@click.argument("key")
@click.argument("value")
def set_value(key: str, value: str):
    """Set a configuration value

    Example: kabu config set default_importance 3
    """
    # Convert value to appropriate type
    if value.isdigit():
        typed_value: str | int = int(value)
    else:
        typed_value = value

    config.set(key, typed_value)
    click.echo(f"Set {key} = {typed_value}")


@cfg.command("get")
@click.argument("key")
def get_value(key: str):
    """Get a configuration value"""
    value = config.get(key)
    if value is None:
        click.echo(f"Key '{key}' not found")
    else:
        click.echo(value)


@cfg.command("path")
def path():
    """Show config file path"""
    click.echo(config.get_config_path())


# Index configuration subcommands
@cfg.group("index")
def index_config():
    """Manage custom index configuration"""
    pass


@index_config.command("list")
def list_indices():
    """List all available index codes"""
    from pykabu.sources import nikkei225

    all_indices = nikkei225.get_all_known_indices()
    default_indices = nikkei225.get_default_indices()
    custom_indices = config.get_custom_indices()

    click.echo("Available indices:")
    click.echo()
    for code in sorted(all_indices.keys(), key=lambda x: int(x)):
        name = all_indices[code]
        markers = []
        if code in default_indices:
            markers.append("default")
        if code in custom_indices:
            markers.append("custom")
        marker_str = f" ({', '.join(markers)})" if markers else ""
        click.echo(f"  {code}: {name}{marker_str}")
    click.echo()
    click.echo("Use 'kabu config index add CODE' to add custom indices.")


@index_config.command("add")
@click.argument("code")
@click.option("--name", type=str, help="Custom name for the index")
def add_index(code: str, name: str | None):
    """Add a custom index by code

    Example: kabu config index add 212
    """
    from pykabu.sources import nikkei225

    if name is None:
        name = nikkei225.get_all_known_indices().get(code, f"Index {code}")

    config.add_custom_index(code, name)
    click.echo(f"Added index: {code} ({name})")


@index_config.command("remove")
@click.argument("code")
def remove_index(code: str):
    """Remove a custom index"""
    if config.remove_custom_index(code):
        click.echo(f"Removed index: {code}")
    else:
        click.echo(f"Index {code} not found in custom indices")


@index_config.command("clear")
def clear_indices():
    """Clear all custom indices"""
    config.clear_custom_indices()
    click.echo("Cleared all custom indices")


@index_config.command("show")
def show_custom():
    """Show custom indices"""
    custom = config.get_custom_indices()
    if not custom:
        click.echo("No custom indices configured.")
        return
    click.echo("Custom indices:")
    for code, name in custom.items():
        click.echo(f"  {code}: {name}")
