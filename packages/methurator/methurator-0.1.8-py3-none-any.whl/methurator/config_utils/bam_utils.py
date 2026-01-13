import rich_click as click
from methurator.config_utils.validation_utils import ensure_coordinated_sorted


def bam_to_list(configs):

    # Loops over the bam files specified and ensures are csorted
    csorted_bams = []
    for bam_file in configs.bam:
        try:
            csorted_bams.append(ensure_coordinated_sorted(bam_file, configs))
        except ValueError as e:
            raise click.UsageError(f"{e}")
    return csorted_bams
