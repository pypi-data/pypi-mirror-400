from methurator.downsample_utils.run_processing import run_processing
from methurator.downsample_utils.yaml_summary import generate_yaml_summary
from methurator.config_utils.config_formatter import ConfigFormatter
from methurator.config_utils.config_validator import validate_parameters, available_cpus
from methurator.config_utils.bam_utils import bam_to_list
from methurator.config_utils.verbose_utils import vprint
from methurator.config_utils.validation_utils import validate_dependencies
import rich_click as click
from rich.console import Console
from rich.panel import Panel
import os
import shutil
import importlib.metadata

console = Console()


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.argument(
    "bams",
    type=click.Path(exists=True),
    required=True,
    nargs=-1,
    help="Path to a single .bam file or to multiple ones (e.g. files/*.bam).",
)
@click.option(
    "--outdir",
    "-o",
    type=click.Path(),
    default="output",
    help="Default ./output directory.",
)
@click.option(
    "--fasta",
    type=click.Path(exists=True),
    help="Fasta file of the reference genome used to align the samples. "
    "If not provided, it will download it according to the specified genome.",
)
@click.option(
    "--genome",
    type=click.Choice(["hg19", "hg38", "GRCh37", "GRCh38", "mm10", "mm39"]),
    default=None,
    help="Genome used to align the samples.",
)
@click.option(
    "--downsampling-percentages",
    "-ds",
    default="0.1,0.2,0.4,0.6,0.8",
    help="Percentages used to downsample the .bam file. Default: 0.1,0.25,0.5,0.75",
)
@click.option(
    "--minimum-coverage",
    "-mc",
    default="3",
    help="Minimum CpG coverage to estimate sequencing saturation. "
    "It can be either a single integer or a list of integers (e.g 1,3,5). Default: 3",
)
@click.option(
    "--rrbs",
    is_flag=True,
    default=True,
    help="If set to True, MethylDackel extract will consider the RRBS nature of the data "
    "adding the --keepDupes flag. Default: True",
)
@click.option(
    "--threads",
    "-@",
    type=int,
    default=lambda: max(1, available_cpus() - 2),
    help="Number of threads to use. Default: all available threads - 2.",
)
@click.option(
    "--keep-temporary-files",
    "-k",
    is_flag=True,
    help="If set to True, temporary files will be kept after the analysis. Default: False",
)
@click.option("--verbose", is_flag=True, help="Enable verbose logging.")
@click.version_option(importlib.metadata.version("methurator"))
def downsample(bams, **kwargs):

    # Import the parameters and validate them
    kwargs["bam"] = bams
    configs = ConfigFormatter(**kwargs)
    validate_parameters(configs)

    # Print I/O parameters
    params_text = ""
    params_text += f"[purple]Output directory:[/purple] [blue]{configs.outdir}[/blue]\n"
    if configs.fasta is not None:
        params_text += (
            f"[purple]Reference FASTA:[/purple] [blue]{configs.fasta}[/blue]\n"
        )
    if configs.genome is not None:
        params_text += f"[purple]Genome:[/purple] [blue]{configs.genome}[/blue]\n"
    params_text += f"[purple]Downsampling percentages:[/purple] [blue]{configs.downsampling_percentages}[/blue]\n"
    params_text += f"[purple]Minimum coverage values:[/purple] [blue]{configs.minimum_coverage}[/blue]\n"
    params_text += f"[purple]rrbs:[/purple] [blue]{configs.rrbs}[/blue]\n"
    params_text += f"[purple]Threads:[/purple] [blue]{configs.threads}[/blue]\n"
    params_text += f"[purple]Keep temporary files:[/purple] [blue]{configs.keep_temporary_files}[/blue]"
    console.print(
        Panel(
            params_text,
            title="📌 [bold cyan]Input / Output Parameters[/bold cyan]",
            border_style="cyan",
            expand=False,
        )
    )

    # Check that required external tools are installed
    validate_dependencies()

    # Load bam file(s) and run the downsampling
    csorted_bams = bam_to_list(configs)
    cpgs_df, reads_df = run_processing(csorted_bams, configs)
    reads_df.to_csv(
        os.path.join(configs.outdir, "methurator_reads_summary.csv"), index=False
    )
    cpgs_df.to_csv(
        os.path.join(configs.outdir, "methurator_cpgs_summary.csv"), index=False
    )
    generate_yaml_summary(reads_df, cpgs_df, configs, configs.bam)
    vprint(f"[bold] ✅ Dumped summary files to {configs.outdir}.[/bold]", True)

    # Clean-up
    if not configs.keep_temporary_files:
        shutil.rmtree(os.path.join(configs.outdir, "bams"))
        shutil.rmtree(os.path.join(configs.outdir, "covs"))
