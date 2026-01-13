from methurator.plot_utils.plot_curve import plot_curve
import rich_click as click
from methurator.config_utils.config_formatter import ConfigFormatter
from methurator.config_utils.validation_utils import validate_summary_yaml
from rich.console import Console
from rich.panel import Panel
import importlib.metadata

console = Console()


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option(
    "--summary",
    "-s",
    type=click.Path(exists=True),
    required=True,
    help="File (yml) containing summary results of downsample command.",
)
@click.option(
    "--outdir",
    "-o",
    type=click.Path(),
    default="output",
    help="Default output directory.",
)
@click.option("--verbose", is_flag=True, help="Enable verbose logging.")
@click.version_option(importlib.metadata.version("methurator"))
def plot(**kwargs):
    """Plot the sequencing saturation curve from downsampling results."""
    # Import and validate params
    configs = ConfigFormatter(**kwargs)
    validate_summary_yaml(configs.summary)

    # Print I/O parameters
    params_text = ""
    params_text += f"[purple]Summary file:[/purple] [blue]{configs.summary}[/blue]\n"
    params_text += f"[purple]Output directory:[/purple] [blue]{configs.outdir}[/blue]"
    console.print(
        Panel(
            params_text,
            title="📌 [bold cyan]Input / Output Parameters[/bold cyan]",
            border_style="cyan",
            expand=False,
        )
    )

    # Fit the model and plot the saturation curve
    plot_curve(configs)
