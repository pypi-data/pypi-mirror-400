import rich_click as click
import os
from methurator.config_utils.validation_utils import (
    mincoverage_checker,
    percentage_checker,
    validate_reference,
)
from methurator.config_utils.verbose_utils import vprint


def validate_parameters(configs):

    # Enforce that at least one of --fasta or --genome is provided
    if configs.fasta is None and configs.genome is None:
        raise click.UsageError(
            "Error: you must provide in input either --fasta or --genome"
        )

    # Enforce that at least one of bam file is provided
    if configs.bam is None or len(configs.bam) == 0:
        raise click.UsageError("Error: you must provide at least one BAM file")

    # Check that downsampling percentages and minimum coverage values are valid
    try:
        configs.percentages = percentage_checker(configs.downsampling_percentages)
    except ValueError as e:
        raise click.UsageError(f"{e}")
    try:
        configs.coverages = mincoverage_checker(configs.minimum_coverage)
    except ValueError as e:
        raise click.UsageError(f"{e}")

    # Run checks on fasta file if provided or download it
    try:
        configs.fasta = validate_reference(configs)
    except ValueError as e:
        raise click.UsageError(f"{e}")

    # Create output directory if it doesn't exist
    if not os.path.exists(configs.outdir):
        os.makedirs(configs.outdir, exist_ok=True)
        vprint(
            f"[bold]Created output directory {configs.outdir}...[/bold]",
            configs.verbose,
        )


def available_cpus():
    try:
        # Linux-only: returns the set of CPU IDs this process
        # is allowed to run on (respects SLURM / cgroups / taskset)
        return len(os.sched_getaffinity(0))
    except AttributeError:
        # Fallback for non-Linux systems or Python builds
        # without sched_getaffinity support
        return os.cpu_count()
