from methurator.downsample_utils.methyldackel import run_methyldackel
from methurator.downsample_utils.subsample_bam import subsample_bam
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    MofNCompleteColumn,
)
import pandas as pd
import os


def run_processing(csorted_bams, configs):

    # Create empty dataframes to store results
    reads_df = pd.DataFrame(columns=["Sample", "Percentage", "Read_Count"])
    cpgs_df = pd.DataFrame(columns=["Sample", "Percentage", "Coverage", "CpG_Count"])

    # Calculate total steps for progress tracking
    total_bams = len(csorted_bams)
    total_percentages = len(configs.percentages)

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        refresh_per_second=10,
    ) as progress:

        # Loop over bam files
        for bam_idx, bam in enumerate(csorted_bams):
            bam_name = os.path.basename(bam)

            # BAM file progress task
            bam_task = progress.add_task(
                f"[green]BAM {bam_idx + 1}/{total_bams}: {bam_name}",
                total=total_percentages,
            )

            for pct in configs.percentages:
                # Update description to show current subsample level
                progress.update(
                    bam_task,
                    description=f"[green]BAM {bam_idx + 1}/{total_bams}: {bam_name} @ {pct:.0%}",
                )

                # Subsampling step
                subsample_task = progress.add_task(
                    "  [yellow]Subsampling...",
                    total=None,  # Indeterminate
                )
                results_subsampling_bam, sub_bam = subsample_bam(
                    bam, pct, configs.outdir
                )
                reads_df.loc[len(reads_df)] = results_subsampling_bam
                progress.remove_task(subsample_task)

                # MethylDackel step
                methyldackel_task = progress.add_task(
                    "  [magenta]Running MethylDackel...",
                    total=None,  # Indeterminate
                )
                cpgs_df = run_methyldackel(sub_bam, pct, configs, cpgs_df)
                progress.remove_task(methyldackel_task)

                # Update progress
                progress.advance(bam_task)

            # Mark BAM as complete and remove its task
            progress.remove_task(bam_task)

    return cpgs_df, reads_df
