import rich_click as click
from methurator.config_utils.verbose_utils import vprint
from methurator.config_utils.download_reference import get_reference
import os
import shutil
import subprocess
import sys
import pysam
from rich.console import Console
from rich.panel import Panel
import yaml


def validate_dependencies():
    """Check that required external tools (samtools, MethylDackel) are installed."""
    console = Console()
    missing = []

    if shutil.which("samtools") is None:
        missing.append("samtools")

    if shutil.which("MethylDackel") is None:
        missing.append("MethylDackel")

    if missing:
        tools_list = ", ".join(missing)
        console.print(
            Panel(
                f"[red bold]Missing required dependencies: {tools_list}[/red bold]",
                title="[red]Dependency Error[/red]",
                border_style="red",
                expand=False,
            )
        )
        sys.exit(1)


def mincoverage_checker(coverages):
    """
    Converts a comma-separated string into a list of integers.
    """
    values = coverages.split(",")
    list_coverages = []

    for x in values:
        x = x.strip()
        if not x.isdigit():
            raise click.UsageError(
                f"Invalid minimum coverage value: '{x}'. All minimum coverage must be integers."
            )
        if int(x) == 0:
            vprint(
                f"[yellow]⚠️ Warning: coverage values must be at least >=1, '{x}' was ignored.[/yellow]",
                True,
            )
        else:
            list_coverages.append(int(x))

    return list_coverages


def percentage_checker(percentages):
    """
    Converts a comma-separated string into a list of floats.
    """
    list_percentages = [float(x.strip()) for x in percentages.split(",")]

    if any(p == 0 for p in list_percentages):
        raise click.UsageError("Percentages must be between > 0.")

    if len(list_percentages) < 4:
        raise click.UsageError("At least four percentages must be provided.")

    # And now add 1 if not persent to the list
    # to calculate CpG number on original sample
    if 1 not in list_percentages:
        list_percentages = list_percentages + [1]

    return list_percentages


def validate_reference(configs):

    if configs.fasta and configs.genome:
        vprint(
            "[yellow]⚠️ Both --fasta and --genome provided. Using the provided fasta file.[/yellow]",
            configs.verbose,
        )

    if configs.fasta:
        if not (configs.fasta.endswith(".fa") or configs.fasta.endswith(".fasta")):
            raise click.UsageError(
                "The fasta file provided must end with .fa or .fasta."
            )
        if not os.path.exists(configs.fasta):
            raise click.UsageError(f"The fasta file '{configs.fasta}' does not exist.")
        return configs.fasta
    else:
        fasta_file = get_reference(configs)
        return fasta_file


def ensure_coordinated_sorted(bam_file, configs):

    # Check if file exists
    if not os.path.exists(bam_file):
        raise click.UsageError(f"The file '{bam_file}' does not exist.")

    # Check if file ends with .bam
    if not bam_file.endswith(".bam"):
        raise click.UsageError("The input file must end with .bam")

    with pysam.AlignmentFile(bam_file, "rb") as bam:
        sort_order = bam.header.get("HD", {}).get("SO", None)

    if sort_order == "coordinate":
        return bam_file

    vprint("🔄 BAM file is not coordinate-sorted. Sorting now...", configs.verbose)
    out = bam_file.replace(".bam", ".csorted.bam")
    cmd = ["samtools", "sort", "-o", out, bam_file]

    # Run samtools
    subprocess.run(cmd)

    return out


def validate_summary_yaml(yaml_path):
    """
    Validate that the summary YAML file follows the expected structure.
    """
    required_top_keys = ["methurator_summary"]
    required_metadata_keys = [
        "date_generated",
        "methurator_version",
        "command",
        "options",
    ]
    required_options_keys = [
        "bam_files",
        "outdir",
        "fasta",
        "genome",
        "downsampling_percentages",
        "minimum_coverage",
        "rrbs",
        "threads",
        "keep_temporary_files",
    ]

    with open(yaml_path) as f:
        content = yaml.safe_load(f)

    # Top-level key
    if not all(k in content for k in required_top_keys):
        raise click.UsageError(
            f"YAML file must contain top-level keys: {required_top_keys}"
        )

    # Metadata
    summary = content["methurator_summary"]
    metadata = summary.get("metadata")
    if not metadata:
        raise click.UsageError("Missing 'metadata' section in methurator_summary")
    if not all(k in metadata for k in required_metadata_keys):
        raise click.UsageError(
            f"'metadata' must contain keys: {required_metadata_keys}"
        )

    options = metadata.get("options", {})
    if not all(k in options for k in required_options_keys):
        raise click.UsageError(
            f"'metadata.options' must contain keys: {required_options_keys}"
        )

    # Reads summary
    reads_summary = summary.get("reads_summary")
    if reads_summary is None:
        raise click.UsageError("Missing 'reads_summary' section")

    # cpgs summary
    cpgs_summary = summary.get("cpgs_summary")
    if cpgs_summary is None:
        raise click.UsageError("Missing 'cpgs_summary' section")

    # Saturation analysis
    saturation_analysis = summary.get("saturation_analysis")
    if saturation_analysis is None:
        raise click.UsageError("Missing 'saturation_analysis' section")
