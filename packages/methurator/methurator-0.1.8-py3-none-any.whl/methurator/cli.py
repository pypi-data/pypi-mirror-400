import rich_click as click
from methurator.plot import plot
from methurator.downsample import downsample
import importlib.metadata


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.version_option(importlib.metadata.version("methurator"))
@click.command_panel("Commands")
@click.option_panel("Arguments")
@click.option_panel("Options")
@click.rich_config(
    {
        "options_table_column_types": ["opt_long", "opt_short", "help"],
        "options_table_help_sections": ["help", "metavar", "required", "default"],
    }
)
def entry_point():
    """Estimate sequencing saturation for reduced-representation bisulfite sequencing (RRBS) data."""
    pass


# Register the 2 subcommands: downsample and plot
entry_point.add_command(plot)
entry_point.add_command(downsample)

if __name__ == "__main__":
    entry_point()
